from decimal import Decimal, InvalidOperation

from django.db import connection, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from apps.customers.auth import CustomerJWTAuthentication
from apps.customers.permissions import IsAuthenticatedCustomer

from .models import WorkOrder, WorkOrderProduct, WorkOrderService
from .serializers import (
    WorkOrderCustomerSerializer,
    WorkOrderProductSerializer,
    WorkOrderSerializer,
    WorkOrderServiceSerializer,
)

PRODUCT_STOCK_COLUMN = "stock_qty"


def _to_decimal(value, field_name: str) -> Decimal:
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{field_name} inválido.")
    if d <= 0:
        raise ValueError(f"{field_name} debe ser > 0.")
    return d


def _ensure_work_order_not_cancelled(work_order_id: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute("select status from public.work_orders where work_order_id = %s", [work_order_id])
        row = cursor.fetchone()
        if not row:
            raise ValueError("Work order no existe.")
        if (row[0] or "").strip().lower() == "cancelled":
            raise ValueError("No se puede modificar una work order cancelada.")


def _lock_product_and_get_stock(product_id: str) -> Decimal:
    with connection.cursor() as cursor:
        cursor.execute(
            f"select {PRODUCT_STOCK_COLUMN} from public.products where product_id = %s for update",
            [product_id],
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError("Producto no existe.")
        return Decimal(str(row[0] or 0))


def _update_product_stock(product_id: str, new_stock: Decimal) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            update public.products
            set {PRODUCT_STOCK_COLUMN} = %s,
                updated_at = now()
            where product_id = %s
            """,
            [str(new_stock), product_id],
        )


class OpenAppointmentsAdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def list(self, request):
        statuses = request.query_params.get("statuses")
        if statuses:
            allowed = [s.strip() for s in statuses.split(",") if s.strip()]
        else:
            allowed = ["pending", "scheduled", "accepted", "in_progress"]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                  a.appointment_id,
                  a.status,
                  a.scheduled_start,
                  a.requested_work,
                  c.customer_id,
                  c.full_name,
                  c.email,
                  v.vehicle_id,
                  v.plate,
                  v.make,
                  v.model,
                  v.year
                from public.appointments a
                join public.customers c on c.customer_id = a.customer_id
                join public.vehicles v on v.vehicle_id = a.vehicle_id
                where a.status = any(%s)
                order by a.scheduled_start asc
                limit 200
                """,
                [allowed],
            )
            rows = cursor.fetchall()

        data = []
        for r in rows:
            data.append(
                {
                    "appointment_id": r[0],
                    "status": r[1],
                    "scheduled_start": r[2],
                    "requested_work": r[3],
                    "customer": {"customer_id": r[4], "full_name": r[5], "email": r[6]},
                    "vehicle": {"vehicle_id": r[7], "plate": r[8], "make": r[9], "model": r[10], "year": r[11]},
                }
            )

        return Response(data, status=200)


class WorkOrderAdminViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = WorkOrder.objects.select_related("customer", "vehicle", "appointment").all()

        appointment_id = self.request.query_params.get("appointment_id")
        if appointment_id:
            qs = qs.filter(appointment_id=appointment_id)

        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        status_q = self.request.query_params.get("status")
        if status_q:
            qs = qs.filter(status__iexact=status_q.strip())

        return qs

    @action(detail=False, methods=["post"], url_path="create-from-appointment")
    def create_from_appointment(self, request):
        appointment_id = (request.data or {}).get("appointment_id")
        if not appointment_id:
            return Response({"detail": "appointment_id es requerido."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "select customer_id, vehicle_id from public.appointments where appointment_id = %s",
                [str(appointment_id)],
            )
            row = cursor.fetchone()
            if not row:
                return Response({"detail": "Cita no existe."}, status=404)

            customer_id, vehicle_id = row[0], row[1]

            cursor.execute(
                "select work_order_id from public.work_orders where appointment_id = %s",
                [str(appointment_id)],
            )
            exists = cursor.fetchone()
            if exists:
                wo_id = exists[0]
                wo = WorkOrder.objects.select_related("customer", "vehicle", "appointment").get(work_order_id=wo_id)
                return Response(self.get_serializer(wo).data, status=200)

            cursor.execute(
                """
                insert into public.work_orders
                  (appointment_id, customer_id, vehicle_id, status, authorization_status, opened_at, created_at, updated_at)
                values
                  (%s, %s, %s, 'open', 'pending', now(), now(), now())
                returning work_order_id
                """,
                [str(appointment_id), str(customer_id), str(vehicle_id)],
            )
            wo_id = cursor.fetchone()[0]

        wo = WorkOrder.objects.select_related("customer", "vehicle", "appointment").get(work_order_id=wo_id)
        return Response(self.get_serializer(wo).data, status=201)

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        customer_id = data.get("customer_id")
        vehicle_id = data.get("vehicle_id")
        if not customer_id:
            return Response({"detail": "customer_id es requerido."}, status=400)
        if not vehicle_id:
            return Response({"detail": "vehicle_id es requerido."}, status=400)

        appointment_id = data.get("appointment_id") or None
        status_v = (data.get("status") or "open").strip()
        auth_status = (data.get("authorization_status") or "pending").strip()
        customer_symptoms = (data.get("customer_symptoms") or "").strip() or None
        notes = (data.get("notes") or "").strip() or None

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.work_orders
                  (appointment_id, customer_id, vehicle_id, status, customer_symptoms,
                   authorization_status, opened_at, notes, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s,
                   %s, now(), %s, now(), now())
                returning work_order_id
                """,
                [appointment_id, customer_id, vehicle_id, status_v, customer_symptoms, auth_status, notes],
            )
            work_order_id = cursor.fetchone()[0]

        wo = WorkOrder.objects.select_related("customer", "vehicle", "appointment").get(work_order_id=work_order_id)
        return Response(self.get_serializer(wo).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        wo = self.get_object()
        data = request.data or {}

        allowed = {
            "status",
            "customer_symptoms",
            "diagnosis",
            "estimated_total",
            "authorization_status",
            "authorized_at",
            "authorized_by",
            "assigned_mechanic_id",
            "closed_at",
            "notes",
        }
        for k in data.keys():
            if k not in allowed:
                return Response({"detail": f"No permitido: {k}"}, status=403)

        sets = []
        params = []

        if "status" in data:
            sets.append("status = %s")
            params.append((data.get("status") or "").strip())

        if "customer_symptoms" in data:
            sets.append("customer_symptoms = %s")
            params.append((data.get("customer_symptoms") or "").strip() or None)

        if "diagnosis" in data:
            sets.append("diagnosis = %s")
            params.append((data.get("diagnosis") or "").strip() or None)

        if "estimated_total" in data:
            sets.append("estimated_total = %s")
            params.append(data.get("estimated_total"))

        if "authorization_status" in data:
            sets.append("authorization_status = %s")
            params.append((data.get("authorization_status") or "").strip())

        if "authorized_at" in data:
            sets.append("authorized_at = %s")
            params.append(data.get("authorized_at") or None)

        if "authorized_by" in data:
            sets.append("authorized_by = %s")
            params.append((data.get("authorized_by") or "").strip() or None)

        if "assigned_mechanic_id" in data:
            sets.append("assigned_mechanic_id = %s")
            params.append(data.get("assigned_mechanic_id") or None)

        if "closed_at" in data:
            sets.append("closed_at = %s")
            params.append(data.get("closed_at") or None)

        if "notes" in data:
            sets.append("notes = %s")
            params.append((data.get("notes") or "").strip() or None)

        if not sets:
            wo.refresh_from_db()
            return Response(self.get_serializer(wo).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(wo.work_order_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.work_orders set {', '.join(sets)} where work_order_id = %s",
                params,
            )

        wo.refresh_from_db()
        wo = WorkOrder.objects.select_related("customer", "vehicle", "appointment").get(work_order_id=wo.work_order_id)
        return Response(self.get_serializer(wo).data, status=200)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        wo = self.get_object()
        wo_id = str(wo.work_order_id)

        with connection.cursor() as cursor:
            cursor.execute(
                "select work_order_id from public.work_orders where work_order_id = %s for update",
                [wo_id],
            )
            locked = cursor.fetchone()
            if not locked:
                return Response({"detail": "Work order no existe."}, status=404)

            cursor.execute(
                "select product_id, qty from public.work_order_products where work_order_id = %s",
                [wo_id],
            )
            prod_lines = cursor.fetchall() or []

            for product_id, qty in prod_lines:
                if not product_id:
                    continue

                cursor.execute(
                    f"select {PRODUCT_STOCK_COLUMN} from public.products where product_id = %s for update",
                    [str(product_id)],
                )
                pr = cursor.fetchone()
                if pr is None:
                    continue

                current_stock = Decimal(str(pr[0] or 0))
                cursor.execute(
                    f"""
                    update public.products
                    set {PRODUCT_STOCK_COLUMN} = %s,
                        updated_at = now()
                    where product_id = %s
                    """,
                    [str(current_stock + Decimal(str(qty))), str(product_id)],
                )

            cursor.execute("delete from public.work_order_products where work_order_id = %s", [wo_id])
            cursor.execute("delete from public.work_order_services where work_order_id = %s", [wo_id])
            cursor.execute("delete from public.work_orders where work_order_id = %s", [wo_id])

        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkOrderCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkOrderCustomerSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        customer = self.request.user
        return (
            WorkOrder.objects.select_related("vehicle", "appointment")
            .prefetch_related("service_lines__service", "product_lines__product")
            .filter(customer_id=customer.customer_id)
            .order_by("-created_at")
        )


class WorkOrderServiceAdminViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderServiceSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = WorkOrderService.objects.select_related("work_order", "service").all()
        work_order_id = self.request.query_params.get("work_order_id")
        if work_order_id:
            qs = qs.filter(work_order_id=work_order_id)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        work_order_id = data.get("work_order_id")
        if not work_order_id:
            return Response({"detail": "work_order_id es requerido."}, status=400)

        try:
            _ensure_work_order_not_cancelled(str(work_order_id))
            qty = _to_decimal(data.get("qty", "1"), "qty")
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        unit_price_raw = data.get("unit_price", "0")
        try:
            unit_price = Decimal(str(unit_price_raw))
        except Exception:
            return Response({"detail": "unit_price inválido."}, status=400)
        if unit_price < 0:
            return Response({"detail": "unit_price no puede ser negativo."}, status=400)

        service_id = data.get("service_id") or None
        desc = (data.get("description") or "").strip() or None
        mechanic_id = data.get("mechanic_id") or None
        status_v = (data.get("status") or "pending").strip()
        started_at = data.get("started_at") or None
        completed_at = data.get("completed_at") or None

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.work_order_services
                  (work_order_id, service_id, description, qty, unit_price, mechanic_id, status,
                   started_at, completed_at, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, %s, %s,
                   %s, %s, now(), now())
                returning work_order_service_id
                """,
                [work_order_id, service_id, desc, str(qty), str(unit_price), mechanic_id, status_v, started_at, completed_at],
            )
            line_id = cursor.fetchone()[0]

        line = WorkOrderService.objects.select_related("work_order", "service").get(work_order_service_id=line_id)
        return Response(self.get_serializer(line).data, status=201)


class WorkOrderProductAdminViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderProductSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = WorkOrderProduct.objects.select_related("work_order", "product").all()
        work_order_id = self.request.query_params.get("work_order_id")
        if work_order_id:
            qs = qs.filter(work_order_id=work_order_id)
        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data or {}
        work_order_id = data.get("work_order_id")
        product_id = data.get("product_id")

        if not work_order_id:
            return Response({"detail": "work_order_id es requerido."}, status=400)
        if not product_id:
            return Response({"detail": "product_id es requerido."}, status=400)

        try:
            _ensure_work_order_not_cancelled(str(work_order_id))
            qty = _to_decimal(data.get("qty", "1"), "qty")
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        unit_price_raw = data.get("unit_price", "0")
        try:
            unit_price = Decimal(str(unit_price_raw))
        except Exception:
            return Response({"detail": "unit_price inválido."}, status=400)
        if unit_price < 0:
            return Response({"detail": "unit_price no puede ser negativo."}, status=400)

        desc = (data.get("description") or "").strip() or None

        try:
            current_stock = _lock_product_and_get_stock(str(product_id))
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        if current_stock < qty:
            return Response({"detail": "Stock insuficiente para este producto."}, status=409)

        _update_product_stock(str(product_id), current_stock - qty)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.work_order_products
                  (work_order_id, product_id, description, qty, unit_price, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, now(), now())
                returning work_order_product_id
                """,
                [work_order_id, product_id, desc, str(qty), str(unit_price)],
            )
            line_id = cursor.fetchone()[0]

        line = WorkOrderProduct.objects.select_related("work_order", "product").get(work_order_product_id=line_id)
        return Response(self.get_serializer(line).data, status=201)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        line = self.get_object()
        data = request.data or {}

        try:
            _ensure_work_order_not_cancelled(str(line.work_order_id))
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        sets = []
        params = []

        if "description" in data:
            sets.append("description = %s")
            params.append((data.get("description") or "").strip() or None)

        if "unit_price" in data:
            unit_price_raw = data.get("unit_price", "0")
            try:
                unit_price = Decimal(str(unit_price_raw))
            except Exception:
                return Response({"detail": "unit_price inválido."}, status=400)
            if unit_price < 0:
                return Response({"detail": "unit_price no puede ser negativo."}, status=400)
            sets.append("unit_price = %s")
            params.append(str(unit_price))

        if "qty" in data:
            try:
                new_qty = _to_decimal(data.get("qty"), "qty")
            except ValueError as e:
                return Response({"detail": str(e)}, status=400)

            old_qty = Decimal(str(line.qty))
            delta = new_qty - old_qty

            if line.product_id:
                try:
                    current_stock = _lock_product_and_get_stock(str(line.product_id))
                except ValueError as e:
                    return Response({"detail": str(e)}, status=404)

                if delta > 0:
                    if current_stock < delta:
                        return Response({"detail": "Stock insuficiente para aumentar la cantidad."}, status=409)
                    _update_product_stock(str(line.product_id), current_stock - delta)
                elif delta < 0:
                    _update_product_stock(str(line.product_id), current_stock + (-delta))

            sets.append("qty = %s")
            params.append(str(new_qty))

        if not sets:
            line.refresh_from_db()
            return Response(self.get_serializer(line).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(line.work_order_product_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.work_order_products set {', '.join(sets)} where work_order_product_id = %s",
                params,
            )

        line.refresh_from_db()
        line = WorkOrderProduct.objects.select_related("work_order", "product").get(work_order_product_id=line.work_order_product_id)
        return Response(self.get_serializer(line).data, status=200)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        line = self.get_object()

        try:
            _ensure_work_order_not_cancelled(str(line.work_order_id))
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        if line.product_id:
            try:
                current_stock = _lock_product_and_get_stock(str(line.product_id))
            except ValueError as e:
                return Response({"detail": str(e)}, status=404)
            _update_product_stock(str(line.product_id), current_stock + Decimal(str(line.qty)))

        with connection.cursor() as cursor:
            cursor.execute(
                "delete from public.work_order_products where work_order_product_id = %s",
                [str(line.work_order_product_id)],
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
