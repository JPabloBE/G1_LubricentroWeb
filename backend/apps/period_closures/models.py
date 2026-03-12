import uuid
from django.db import models


class PeriodClosure(models.Model):
    closure_id = models.UUIDField(primary_key=True, db_column="closure_id", default=uuid.uuid4, editable=False)
    closure_type = models.TextField(db_column="closure_type", default="monthly")
    period_start = models.DateField(db_column="period_start")
    period_end = models.DateField(db_column="period_end")
    folio = models.TextField(db_column="folio", unique=True)
    status = models.TextField(db_column="status", default="closed")

    total_income = models.DecimalField(db_column="total_income", max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(db_column="total_expenses", max_digits=12, decimal_places=2, default=0)
    total_net = models.DecimalField(db_column="total_net", max_digits=12, decimal_places=2, default=0)
    total_sessions = models.IntegerField(db_column="total_sessions", default=0)
    total_movements = models.IntegerField(db_column="total_movements", default=0)
    cash_discrepancies = models.DecimalField(db_column="cash_discrepancies", max_digits=12, decimal_places=2, default=0)

    sales_total = models.DecimalField(db_column="sales_total", max_digits=12, decimal_places=2, default=0)
    payment_total = models.DecimalField(db_column="payment_total", max_digits=12, decimal_places=2, default=0)
    withdrawal_total = models.DecimalField(db_column="withdrawal_total", max_digits=12, decimal_places=2, default=0)
    refund_total = models.DecimalField(db_column="refund_total", max_digits=12, decimal_places=2, default=0)
    adjustment_total = models.DecimalField(db_column="adjustment_total", max_digits=12, decimal_places=2, default=0)

    notes = models.TextField(db_column="notes", null=True, blank=True)
    closed_by = models.UUIDField(db_column="closed_by", null=True, blank=True)
    closed_at = models.DateTimeField(db_column="closed_at", null=True, blank=True)
    reopened_by = models.UUIDField(db_column="reopened_by", null=True, blank=True)
    reopened_at = models.DateTimeField(db_column="reopened_at", null=True, blank=True)
    reopen_reason = models.TextField(db_column="reopen_reason", null=True, blank=True)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "period_closures"
        managed = False
        ordering = ["-period_start"]


class PeriodClosureAudit(models.Model):
    audit_id = models.UUIDField(primary_key=True, db_column="audit_id", default=uuid.uuid4, editable=False)
    closure = models.ForeignKey(
        PeriodClosure,
        to_field="closure_id",
        db_column="closure_id",
        on_delete=models.CASCADE,
        related_name="audit_entries",
    )
    action = models.TextField(db_column="action")
    performed_by = models.UUIDField(db_column="performed_by", null=True, blank=True)
    performed_at = models.DateTimeField(db_column="performed_at")
    notes = models.TextField(db_column="notes", null=True, blank=True)

    class Meta:
        db_table = "period_closure_audit"
        managed = False
        ordering = ["-performed_at"]
