from django.utils import timezone
from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["category_id", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Si la DB tiene defaults (recomendado), esto igual funciona.
        Si la DB NO tiene defaults para created_at/updated_at, los ponemos aquí.
        """
        now = timezone.now()
        # si por algún motivo llegan nulls, los seteamos
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)
        return super().create(validated_data)
