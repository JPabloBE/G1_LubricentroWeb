from django.utils import timezone
from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "service_id",
            "name",
            "description",
            "base_price",
            "estimated_minutes",
            "requires_lift",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["service_id", "created_at", "updated_at"]

    def validate_name(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("El nombre es obligatorio.")
        return v

    def validate_base_price(self, value):
        if value is None:
            return 0
        if value < 0:
            raise serializers.ValidationError("El precio base no puede ser negativo.")
        return value

    def validate_estimated_minutes(self, value):
        if value is None:
            return None
        if value < 0:
            raise serializers.ValidationError("estimated_minutes no puede ser negativo.")
        return value

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = timezone.now()
        return super().update(instance, validated_data)
