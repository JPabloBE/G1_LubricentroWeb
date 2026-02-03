from django.utils import timezone
from rest_framework import serializers
from .models import Category, Product
from urllib.parse import urlparse

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["category_id", "created_at", "updated_at"]

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.category_id", allow_null=True, required=False)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "category_id",
            "category_name",
            "sku",
            "name",
            "description",
            "image_url",    
            "unit_price",
            "cost",
            "stock_qty",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["product_id", "created_at", "updated_at", "category_name"]

    def validate_sku(self, value):
        # Permite null/blank, pero si viene texto lo normalizamos
        if value is None:
            return None
        v = value.strip()
        return v or None

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)

        category_data = validated_data.pop("category", None)
        if category_data:
            validated_data["category_id"] = category_data.get("category_id")

        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = timezone.now()

        category_data = validated_data.pop("category", None)
        if category_data is not None:
            instance.category_id = category_data.get("category_id")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate_image_url(self, value):
        if value is None:
            return None
        v = value.strip()
        if not v:
            return None
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise serializers.ValidationError("image_url debe ser una URL válida (http/https).")
        return v
