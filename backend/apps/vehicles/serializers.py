from rest_framework import serializers

from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    customer_id = serializers.UUIDField(source="customer.customer_id")
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "vehicle_id",
            "customer_id",
            "customer_name",
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
        read_only_fields = ["vehicle_id", "created_at", "updated_at", "customer_name"]

    def validate_plate(self, value: str):
        v = (value or "").strip().upper()
        if not v:
            raise serializers.ValidationError("plate is required.")
        return v

    def validate_image_url(self, value):
        if value is None:
            return None
        v = str(value).strip()
        if not v:
            return None
        if not (v.startswith("http://") or v.startswith("https://")):
            raise serializers.ValidationError("image_url must start with http:// or https://")
        return v
