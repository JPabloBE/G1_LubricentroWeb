from django.db import connection
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from apps.customers.auth import CustomerJWTAuthentication
from apps.customers.permissions import IsAuthenticatedCustomer

from .models import Vehicle
from .serializers import VehicleLiteSerializer, VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = Vehicle.objects.select_related("customer").all().order_by("plate")

        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        plate = self.request.query_params.get("plate")
        if plate:
            qs = qs.filter(plate__icontains=str(plate).strip())

        return qs

    def create(self, request, *args, **kwargs):
        data = request.data or {}

        customer_id = data.get("customer_id")
        plate = (data.get("plate") or "").strip()
        make = (data.get("make") or "").strip() or None
        model = (data.get("model") or "").strip() or None
        year = data.get("year") or None
        vin = (data.get("vin") or "").strip() or None
        color = (data.get("color") or "").strip() or None
        notes = (data.get("notes") or "").strip() or None
        image_url = (data.get("image_url") or "").strip() or None

        if not customer_id:
            return Response({"detail": "customer_id es requerido."}, status=400)
        if not plate:
            return Response({"detail": "plate es requerido."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.vehicles
                  (customer_id, plate, make, model, year, vin, color, notes, image_url, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                returning vehicle_id
                """,
                [customer_id, plate, make, model, year, vin, color, notes, image_url],
            )
            vehicle_id = cursor.fetchone()[0]

        v = Vehicle.objects.select_related("customer").get(vehicle_id=vehicle_id)
        return Response(self.get_serializer(v).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        v = self.get_object()
        data = request.data or {}

        sets = []
        params = []

        if "customer_id" in data:
            customer_id = data.get("customer_id")
            if not customer_id:
                return Response({"detail": "customer_id no puede ser vacío."}, status=400)
            sets.append("customer_id = %s")
            params.append(customer_id)

        if "plate" in data:
            plate = (data.get("plate") or "").strip()
            if not plate:
                return Response({"detail": "plate no puede ser vacío."}, status=400)
            sets.append("plate = %s")
            params.append(plate)

        for field in ["make", "model", "vin", "color", "notes", "image_url"]:
            if field in data:
                val = (data.get(field) or "").strip() or None
                sets.append(f"{field} = %s")
                params.append(val)

        if "year" in data:
            sets.append("year = %s")
            params.append(data.get("year") or None)

        if not sets:
            v.refresh_from_db()
            v = Vehicle.objects.select_related("customer").get(vehicle_id=v.vehicle_id)
            return Response(self.get_serializer(v).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(v.vehicle_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.vehicles set {', '.join(sets)} where vehicle_id = %s",
                params,
            )

        v.refresh_from_db()
        v = Vehicle.objects.select_related("customer").get(vehicle_id=v.vehicle_id)
        return Response(self.get_serializer(v).data, status=200)

    def destroy(self, request, *args, **kwargs):
        v = self.get_object()
        with connection.cursor() as cursor:
            cursor.execute("delete from public.vehicles where vehicle_id = %s", [str(v.vehicle_id)])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerVehicleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VehicleLiteSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        customer = self.request.user
        return Vehicle.objects.filter(customer_id=customer.customer_id).order_by("plate")
