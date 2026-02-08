from django.db import connection
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin

from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):

    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        qs = Vehicle.objects.select_related("customer").all().order_by("-created_at")

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
        plate = (data.get("plate") or "").strip().upper()

        make = (data.get("make") or "").strip() or None
        model = (data.get("model") or "").strip() or None
        year = data.get("year")
        vin = (data.get("vin") or "").strip() or None
        color = (data.get("color") or "").strip() or None
        notes = (data.get("notes") or "").strip() or None

        image_url = (data.get("image_url") or "").strip() or None

        if not customer_id:
            return Response({"detail": "customer_id is required."}, status=400)
        if not plate:
            return Response({"detail": "plate is required."}, status=400)

        # Normalize year
        if year in ("", None):
            year = None
        else:
            try:
                year = int(year)
            except Exception:
                return Response({"detail": "year must be an integer."}, status=400)

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

        vehicle = Vehicle.objects.select_related("customer").get(vehicle_id=vehicle_id)
        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        data = request.data or {}

        sets = []
        params = []

        if "customer_id" in data:
            customer_id = data.get("customer_id")
            if not customer_id:
                return Response({"detail": "customer_id cannot be empty."}, status=400)
            sets.append("customer_id = %s")
            params.append(customer_id)

        if "plate" in data:
            plate = (data.get("plate") or "").strip().upper()
            if not plate:
                return Response({"detail": "plate cannot be empty."}, status=400)
            sets.append("plate = %s")
            params.append(plate)

        if "make" in data:
            make = (data.get("make") or "").strip() or None
            sets.append("make = %s")
            params.append(make)

        if "model" in data:
            model = (data.get("model") or "").strip() or None
            sets.append("model = %s")
            params.append(model)

        if "year" in data:
            year = data.get("year")
            if year in ("", None):
                year = None
            else:
                try:
                    year = int(year)
                except Exception:
                    return Response({"detail": "year must be an integer."}, status=400)
            sets.append("year = %s")
            params.append(year)

        if "vin" in data:
            vin = (data.get("vin") or "").strip() or None
            sets.append("vin = %s")
            params.append(vin)

        if "color" in data:
            color = (data.get("color") or "").strip() or None
            sets.append("color = %s")
            params.append(color)

        if "notes" in data:
            notes = (data.get("notes") or "").strip() or None
            sets.append("notes = %s")
            params.append(notes)

        # NEW
        if "image_url" in data:
            image_url = (data.get("image_url") or "").strip() or None
            sets.append("image_url = %s")
            params.append(image_url)

        if not sets:
            vehicle.refresh_from_db()
            return Response(VehicleSerializer(vehicle).data, status=200)

        sets.append("updated_at = now()")
        params.append(str(vehicle.vehicle_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.vehicles set {', '.join(sets)} where vehicle_id = %s",
                params,
            )

        vehicle.refresh_from_db()
        vehicle = Vehicle.objects.select_related("customer").get(vehicle_id=vehicle.vehicle_id)
        return Response(VehicleSerializer(vehicle).data, status=200)

    def destroy(self, request, *args, **kwargs):
        vehicle = self.get_object()
        with connection.cursor() as cursor:
            cursor.execute("delete from public.vehicles where vehicle_id = %s", [str(vehicle.vehicle_id)])
        return Response(status=status.HTTP_204_NO_CONTENT)
