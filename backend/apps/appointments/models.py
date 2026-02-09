import uuid
from django.db import models

from apps.customers.models import Customer
from apps.vehicles.models import Vehicle
from apps.services.models import Service


class AppointmentSlot(models.Model):
    slot_id = models.UUIDField(primary_key=True, db_column="slot_id", default=uuid.uuid4, editable=False)
    start_at = models.DateTimeField(db_column="start_at")
    end_at = models.DateTimeField(db_column="end_at", null=True, blank=True)
    capacity = models.IntegerField(db_column="capacity")
    is_active = models.BooleanField(db_column="is_active")
    notes = models.TextField(db_column="notes", null=True, blank=True)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "appointment_slots"
        managed = False
        ordering = ["start_at"]

    def __str__(self) -> str:
        return f"{self.start_at}"


class Appointment(models.Model):
    appointment_id = models.UUIDField(primary_key=True, db_column="appointment_id", default=uuid.uuid4, editable=False)

    customer = models.ForeignKey(
        Customer,
        to_field="customer_id",
        db_column="customer_id",
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        to_field="vehicle_id",
        db_column="vehicle_id",
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    service = models.ForeignKey(
        Service,
        to_field="service_id",
        db_column="service_id",
        on_delete=models.RESTRICT,
        related_name="appointments",
    )

    slot = models.ForeignKey(
        AppointmentSlot,
        to_field="slot_id",
        db_column="slot_id",
        on_delete=models.RESTRICT,
        related_name="appointments",
        null=True,
        blank=True,
    )

    scheduled_start = models.DateTimeField(db_column="scheduled_start")
    scheduled_end = models.DateTimeField(db_column="scheduled_end", null=True, blank=True)

    requested_work = models.TextField(db_column="requested_work", null=True, blank=True)
    status = models.TextField(db_column="status")

    assigned_mechanic_id = models.UUIDField(db_column="assigned_mechanic_id", null=True, blank=True)
    created_by = models.UUIDField(db_column="created_by", null=True, blank=True)
    notes = models.TextField(db_column="notes", null=True, blank=True)

    admin_message = models.TextField(db_column="admin_message", null=True, blank=True)
    progress_percent = models.IntegerField(db_column="progress_percent")

    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "appointments"
        managed = False
        ordering = ["-scheduled_start"]

    def __str__(self) -> str:
        return f"{self.appointment_id}"
