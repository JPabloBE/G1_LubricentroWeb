import uuid
from django.db import models


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
