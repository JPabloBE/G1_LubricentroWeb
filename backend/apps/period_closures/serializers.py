from rest_framework import serializers
from .models import PeriodClosure, PeriodClosureAudit


class PeriodClosureAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodClosureAudit
        fields = ["audit_id", "action", "performed_by", "performed_at", "notes"]


class PeriodClosureSerializer(serializers.ModelSerializer):
    audit_entries = PeriodClosureAuditSerializer(many=True, read_only=True)

    class Meta:
        model = PeriodClosure
        fields = [
            "closure_id",
            "closure_type",
            "period_start",
            "period_end",
            "folio",
            "status",
            "total_income",
            "total_expenses",
            "total_net",
            "total_sessions",
            "total_movements",
            "cash_discrepancies",
            "sales_total",
            "payment_total",
            "withdrawal_total",
            "refund_total",
            "adjustment_total",
            "notes",
            "closed_by",
            "closed_at",
            "reopened_by",
            "reopened_at",
            "reopen_reason",
            "created_at",
            "updated_at",
            "audit_entries",
        ]
        read_only_fields = ["closure_id", "created_at", "updated_at"]


class PeriodClosureListSerializer(serializers.ModelSerializer):
    """Serializer ligero para el listado (sin audit)."""
    class Meta:
        model = PeriodClosure
        fields = [
            "closure_id",
            "closure_type",
            "period_start",
            "period_end",
            "folio",
            "status",
            "total_income",
            "total_expenses",
            "total_net",
            "total_sessions",
            "total_movements",
            "cash_discrepancies",
            "closed_by",
            "closed_at",
            "created_at",
        ]
