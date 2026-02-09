import uuid
from django.db import models

from apps.customers.models import Customer


class Vehicle(models.Model):
    vehicle_id = models.UUIDField(primary_key=True, db_column="vehicle_id", default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        Customer,
        to_field="customer_id",
        db_column="customer_id",
        on_delete=models.CASCADE,
        related_name="vehicles",
    )

    plate = models.TextField(db_column="plate")
    make = models.TextField(db_column="make", null=True, blank=True)
    model = models.TextField(db_column="model", null=True, blank=True)
    year = models.IntegerField(db_column="year", null=True, blank=True)
    vin = models.TextField(db_column="vin", null=True, blank=True)
    color = models.TextField(db_column="color", null=True, blank=True)
    notes = models.TextField(db_column="notes", null=True, blank=True)

    image_url = models.TextField(db_column="image_url", null=True, blank=True)

    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "vehicles"
        managed = False
        ordering = ["plate"]

    def __str__(self) -> str:
        return f"{self.plate}"
