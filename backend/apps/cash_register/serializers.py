from rest_framework import serializers
from django.utils import timezone
from .models import CashSession, CashMovement, CashClosing

MOVEMENT_TYPES = {"sale", "payment", "withdrawal", "refund", "adjustment"}


class CashMovementSerializer(serializers.ModelSerializer):
    # FK explícita: acepta UUID como entrada, devuelve UUID como salida
    cash_session_id = serializers.PrimaryKeyRelatedField(
        queryset=CashSession.objects.all(),
        source="cash_session",
    )
    # created_by se setea en la view, solo lectura para el cliente
    created_by = serializers.UUIDField(read_only=True)

    class Meta:
        model  = CashMovement
        fields = [
            "cash_movement_id", "cash_session_id", "movement_type", "amount",
            "work_order_id", "product_id", "product_qty", "description",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["cash_movement_id", "created_at", "updated_at"]

    def validate_movement_type(self, value):
        if value not in MOVEMENT_TYPES:
            raise serializers.ValidationError(
                f"Tipo inválido. Opciones: {', '.join(sorted(MOVEMENT_TYPES))}"
            )
        return value

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("El monto no puede ser cero.")
        return value

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Devolver el UUID crudo en vez del objeto CashSession
        rep["cash_session_id"] = str(instance.cash_session_id)
        return rep


class CashClosingSerializer(serializers.ModelSerializer):
    cash_session_id = serializers.UUIDField(source="cash_session.cash_session_id", read_only=True)

    class Meta:
        model  = CashClosing
        fields = [
            "cash_closing_id", "cash_session_id", "closing_type",
            "theoretical_amount", "actual_amount", "difference",
            "difference_reason", "audit_note", "closed_by", "closed_at", "created_at",
        ]
        read_only_fields = ["cash_closing_id", "cash_session_id", "created_at"]


class CashSessionSerializer(serializers.ModelSerializer):
    movements = CashMovementSerializer(many=True, read_only=True)
    closings  = CashClosingSerializer(many=True, read_only=True)

    class Meta:
        model  = CashSession
        fields = [
            "cash_session_id", "opened_by", "opened_at", "opening_amount", "status",
            "closed_by", "closed_at", "created_at", "updated_at", "movements", "closings",
        ]
        read_only_fields = ["cash_session_id", "opened_at", "status",
                            "closed_by", "closed_at", "created_at", "updated_at"]

    def validate_opening_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto inicial no puede ser negativo.")
        return value

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("opened_at", now)
        validated_data.setdefault("created_at", now)
        validated_data.setdefault("updated_at", now)
        return super().create(validated_data)


class CashSessionListSerializer(serializers.ModelSerializer):
    """Versión liviana para listas — sin movimientos anidados."""
    class Meta:
        model  = CashSession
        fields = [
            "cash_session_id", "opened_by", "opened_at",
            "opening_amount", "status", "closed_at",
        ]
