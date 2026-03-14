import uuid
from django.db import models


class ServiceChangeLog(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        "Service",
        on_delete=models.DO_NOTHING,
        db_column="service_id",
        related_name="change_logs",
    )
    changed_by_id = models.UUIDField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(max_length=20)
    field_name = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "service_change_log"
        ordering = ["-changed_at"]


class Service(models.Model):
    service_id = models.UUIDField(
        primary_key=True,
        db_column="service_id",
        default=uuid.uuid4,
        editable=False,
    )

    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)

    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_minutes = models.IntegerField(blank=True, null=True)
    requires_lift = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "services"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
