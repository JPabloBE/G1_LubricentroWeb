# backend/apps/appointments/views.py
from django.db import connection
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from apps.customers.auth import CustomerJWTAuthentication
from apps.customers.permissions import IsAuthenticatedCustomer
from apps.vehicles.models import Vehicle

from .models import Appointment, AppointmentSlot
from .serializers import (
    AppointmentSerializer,
    AppointmentSlotCustomerSerializer,
    AppointmentSlotSerializer,
)

CLOSED_FOR_CAPACITY = ("cancelled", "rejected")
ALLOWED_STATUSES = ("scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show", "rejected")


def _count_used_capacity(slot_id: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select count(*)
            from public.appointments
            where slot_id = %s
              and coalesce(status,'') not in ('cancelled','rejected')
            """,
            [slot_id],
        )
        return int(cursor.fetchone()[0] or 0)


class AppointmentSlotAdminViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = AppointmentSlot.objects.all().order_by("start_at")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None and str(is_active).lower() in ("true", "false"):
            qs = qs.filter(is_active=(str(is_active).lower() == "true"))
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        start_at = data.get("start_at")
        end_at = data.get("end_at") or None
        capacity = data.get("capacity")
        is_active = data.get("is_active", True)
        notes = (data.get("notes") or "").strip() or None

        if not start_at:
            return Response({"detail": "start_at es requerido."}, status=400)
        if capacity is None:
            return Response({"detail": "capacity es requerido."}, status=400)

        try:
            capacity_int = int(capacity)
            if capacity_int < 1:
                return Response({"detail": "capacity debe ser >= 1."}, status=400)
        except Exception:
            return Response({"detail": "capacity inválido."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.appointment_slots
                  (start_at, end_at, capacity, is_active, notes, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, now(), now())
                returning slot_id
                """,
                [start_at, end_at, capacity_int, bool(is_active), notes],
            )
            slot_id = cursor.fetchone()[0]

        slot = AppointmentSlot.objects.get(slot_id=slot_id)
        return Response(self.get_serializer(slot).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        slot = self.get_object()
        data = request.data or {}

        sets = []
        params = []

        if "start_at" in data:
            v = data.get("start_at")
            if not v:
                return Response({"detail": "start_at no puede ser vacío."}, status=400)
            sets.append("start_at = %s")
            params.append(v)

        if "end_at" in data:
            sets.append("end_at = %s")
            params.append(data.get("end_at") or None)

        if "capacity" in data:
            try:
                cap = int(data.get("capacity"))
                if cap < 1:
                    return Response({"detail": "capacity debe ser >= 1."}, status=400)
            except Exception:
                return Response({"detail": "capacity inválido."}, status=400)
            sets.append("capacity = %s")
            params.append(cap)

        if "is_active" in data:
            sets.append("is_active = %s")
            params.append(bool(data.get("is_active")))

        if "notes" in data:
            sets.append("notes = %s")
            params.append((data.get("notes") or "").strip() or None)

        if not sets:
            slot.refresh_from_db()
            return Response(self.get_serializer(slot).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(slot.slot_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.appointment_slots set {', '.join(sets)} where slot_id = %s",
                params,
            )

        slot.refresh_from_db()
        return Response(self.get_serializer(slot).data, status=200)

    def destroy(self, request, *args, **kwargs):
        slot = self.get_object()
        with connection.cursor() as cursor:
            cursor.execute("delete from public.appointment_slots where slot_id = %s", [str(slot.slot_id)])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerSlotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AppointmentSlotCustomerSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        now = timezone.now()
        return AppointmentSlot.objects.filter(is_active=True, start_at__gte=now).order_by("start_at")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        rows = list(qs)

        result = []
        for s in rows:
            used = _count_used_capacity(str(s.slot_id))
            remaining = max(int(s.capacity) - used, 0)
            if remaining <= 0:
                continue
            result.append(
                {
                    "slot_id": str(s.slot_id),
                    "start_at": s.start_at,
                    "end_at": s.end_at,
                    "remaining_capacity": remaining,
                }
            )
        return Response(result, status=200)


class AppointmentAdminViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = Appointment.objects.select_related("customer", "vehicle", "service", "slot").all().order_by("-scheduled_start")

        status_q = self.request.query_params.get("status")
        if status_q:
            qs = qs.filter(status__iexact=str(status_q).strip())

        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        vehicle_id = self.request.query_params.get("vehicle_id")
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)

        service_id = self.request.query_params.get("service_id")
        if service_id:
            qs = qs.filter(service_id=service_id)

        slot_id = self.request.query_params.get("slot_id")
        if slot_id:
            qs = qs.filter(slot_id=slot_id)

        return qs

    def partial_update(self, request, *args, **kwargs):
        ap = self.get_object()
        data = request.data or {}

        sets = []
        params = []

        if "status" in data:
            v = (data.get("status") or "").strip()
            if v not in ALLOWED_STATUSES:
                return Response({"detail": "status inválido."}, status=400)
            sets.append("status = %s")
            params.append(v)

        if "admin_message" in data:
            sets.append("admin_message = %s")
            params.append((data.get("admin_message") or "").strip() or None)

        if "progress_percent" in data:
            try:
                p = int(data.get("progress_percent"))
            except Exception:
                return Response({"detail": "progress_percent inválido."}, status=400)
            if p < 0 or p > 100:
                return Response({"detail": "progress_percent debe estar entre 0 y 100."}, status=400)
            sets.append("progress_percent = %s")
            params.append(p)

        if "scheduled_end" in data:
            sets.append("scheduled_end = %s")
            params.append(data.get("scheduled_end") or None)

        if "assigned_mechanic_id" in data:
            sets.append("assigned_mechanic_id = %s")
            params.append(data.get("assigned_mechanic_id") or None)

        if not sets:
            ap = Appointment.objects.select_related("customer", "vehicle", "service", "slot").get(appointment_id=ap.appointment_id)
            return Response(self.get_serializer(ap).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(ap.appointment_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.appointments set {', '.join(sets)} where appointment_id = %s",
                params,
            )

        ap.refresh_from_db()
        ap = Appointment.objects.select_related("customer", "vehicle", "service", "slot").get(appointment_id=ap.appointment_id)
        return Response(self.get_serializer(ap).data, status=200)


class AppointmentCustomerViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        customer = self.request.user
        return (
            Appointment.objects.select_related("customer", "vehicle", "service", "slot")
            .filter(customer_id=customer.customer_id)
            .order_by("-scheduled_start")
        )

    def create(self, request, *args, **kwargs):
        customer = request.user
        data = request.data or {}

        forbidden = {"scheduled_end", "scheduled_start", "status", "admin_message", "progress_percent", "customer_id"}
        if any(k in data for k in forbidden):
            return Response({"detail": "No permitido."}, status=403)

        vehicle_id = data.get("vehicle_id")
        service_id = data.get("service_id")
        slot_id = data.get("slot_id")
        requested_work = (data.get("requested_work") or "").strip() or None
        notes = (data.get("notes") or "").strip() or None

        if not vehicle_id:
            return Response({"detail": "vehicle_id es requerido."}, status=400)
        if not service_id:
            return Response({"detail": "service_id es requerido."}, status=400)
        if not slot_id:
            return Response({"detail": "slot_id es requerido."}, status=400)

        try:
            vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({"detail": "Vehículo no existe."}, status=404)

        if str(vehicle.customer_id) != str(customer.customer_id):
            return Response({"detail": "Ese vehículo no pertenece a tu cuenta."}, status=403)

        try:
            slot = AppointmentSlot.objects.get(slot_id=slot_id, is_active=True)
        except AppointmentSlot.DoesNotExist:
            return Response({"detail": "Horario no disponible."}, status=404)

        used = _count_used_capacity(str(slot.slot_id))
        remaining = max(int(slot.capacity) - used, 0)
        if remaining <= 0:
            return Response({"detail": "No hay cupos disponibles para este horario."}, status=409)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.appointments
                  (customer_id, vehicle_id, service_id, slot_id, scheduled_start, scheduled_end,
                   requested_work, status, notes, admin_message, progress_percent, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, %s,
                   %s, 'scheduled', %s, null, 0, now(), now())
                returning appointment_id
                """,
                [
                    str(customer.customer_id),
                    str(vehicle.vehicle_id),
                    service_id,
                    str(slot.slot_id),
                    slot.start_at,
                    slot.end_at,
                    requested_work,
                    notes,
                ],
            )
            appointment_id = cursor.fetchone()[0]

        ap = Appointment.objects.select_related("customer", "vehicle", "service", "slot").get(appointment_id=appointment_id)
        return Response(self.get_serializer(ap).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        ap = self.get_object()
        data = request.data or {}

        forbidden = {
            "status",
            "assigned_mechanic_id",
            "created_by",
            "customer_id",
            "scheduled_end",
            "vehicle_id",
            "service_id",
            "slot_id",
            "scheduled_start",
            "admin_message",
            "progress_percent",
        }
        if any(k in data for k in forbidden):
            return Response({"detail": "No permitido."}, status=403)

        sets = []
        params = []

        if "requested_work" in data:
            sets.append("requested_work = %s")
            params.append((data.get("requested_work") or "").strip() or None)

        if "notes" in data:
            sets.append("notes = %s")
            params.append((data.get("notes") or "").strip() or None)

        if not sets:
            ap = Appointment.objects.select_related("customer", "vehicle", "service", "slot").get(appointment_id=ap.appointment_id)
            return Response(self.get_serializer(ap).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(ap.appointment_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.appointments set {', '.join(sets)} where appointment_id = %s",
                params,
            )

        ap.refresh_from_db()
        ap = Appointment.objects.select_related("customer", "vehicle", "service", "slot").get(appointment_id=ap.appointment_id)
        return Response(self.get_serializer(ap).data, status=200)

    def destroy(self, request, *args, **kwargs):
        ap = self.get_object()

        current_status = (ap.status or "").strip().lower()
        if current_status != "scheduled":
            return Response(
                {"detail": "No podés cancelar una cita que ya fue aceptada o procesada por el taller."},
                status=403,
            )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                update public.appointments
                set status = 'cancelled', updated_at = now()
                where appointment_id = %s and customer_id = %s and status = 'scheduled'
                """,
                [str(ap.appointment_id), str(request.user.customer_id)],
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
