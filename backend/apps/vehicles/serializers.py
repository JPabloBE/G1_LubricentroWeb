from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "vehicle_id",
            "customer_id",
            "customer_name",
            "customer_email",
            "plate",
            "make",
            "model",
            "year",
            "vin",
            "color",
            "notes",
            "image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["vehicle_id", "created_at", "updated_at"]


class VehicleLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["vehicle_id", "plate", "make", "model", "year", "image_url"]
