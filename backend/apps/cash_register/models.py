import uuid
from django.db import models


class CashSession(models.Model):
    cash_session_id = models.UUIDField(primary_key=True, db_column="cash_session_id", default=uuid.uuid4, editable=False)
    opened_by       = models.UUIDField(db_column="opened_by")
    opened_at       = models.DateTimeField(db_column="opened_at")
    opening_amount  = models.DecimalField(db_column="opening_amount", max_digits=12, decimal_places=2)
    status          = models.TextField(db_column="status", default="open")
    closed_by       = models.UUIDField(db_column="closed_by", null=True, blank=True)
    closed_at       = models.DateTimeField(db_column="closed_at", null=True, blank=True)
    created_at      = models.DateTimeField(db_column="created_at")
    updated_at      = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "cash_sessions"
        managed  = False
        ordering = ["-opened_at"]

    def __str__(self):
        return f"Caja {self.cash_session_id} ({self.status})"


class CashMovement(models.Model):
    cash_movement_id = models.UUIDField(primary_key=True, db_column="cash_movement_id", default=uuid.uuid4, editable=False)
    cash_session     = models.ForeignKey(
        CashSession,
        to_field="cash_session_id",
        db_column="cash_session_id",
        on_delete=models.PROTECT,
        related_name="movements",
    )
    movement_type    = models.TextField(db_column="movement_type")
    amount           = models.DecimalField(db_column="amount", max_digits=12, decimal_places=2)
    work_order_id    = models.UUIDField(db_column="work_order_id", null=True, blank=True)
    product_id       = models.UUIDField(db_column="product_id", null=True, blank=True)
    product_qty      = models.DecimalField(db_column="product_qty", max_digits=12, decimal_places=2, null=True, blank=True)
    description      = models.TextField(db_column="description", null=True, blank=True)
    created_by       = models.UUIDField(db_column="created_by")
    created_at       = models.DateTimeField(db_column="created_at")
    updated_at       = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "cash_movements"
        managed  = False
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movement_type} {self.amount}"


class CashClosing(models.Model):
    cash_closing_id    = models.UUIDField(primary_key=True, db_column="cash_closing_id", default=uuid.uuid4, editable=False)
    cash_session       = models.ForeignKey(
        CashSession,
        to_field="cash_session_id",
        db_column="cash_session_id",
        on_delete=models.PROTECT,
        related_name="closings",
    )
    closing_type       = models.TextField(db_column="closing_type")
    theoretical_amount = models.DecimalField(db_column="theoretical_amount", max_digits=12, decimal_places=2)
    actual_amount      = models.DecimalField(db_column="actual_amount", max_digits=12, decimal_places=2)
    difference         = models.DecimalField(db_column="difference", max_digits=12, decimal_places=2)
    difference_reason  = models.TextField(db_column="difference_reason", null=True, blank=True)
    audit_note         = models.TextField(db_column="audit_note", null=True, blank=True)
    closed_by          = models.UUIDField(db_column="closed_by")
    closed_at          = models.DateTimeField(db_column="closed_at")
    created_at         = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "cash_closings"
        managed  = False
        ordering = ["-closed_at"]

    def __str__(self):
        return f"Cierre {self.closing_type} {self.closed_at}"
