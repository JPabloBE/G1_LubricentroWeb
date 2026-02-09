import uuid
from django.db import models

from apps.appointments.models import Appointment
from apps.customers.models import Customer
from apps.services.models import Service
from apps.vehicles.models import Vehicle
from apps.catalog.models import Product


class WorkOrder(models.Model):
    work_order_id = models.UUIDField(primary_key=True, db_column="work_order_id", default=uuid.uuid4, editable=False)

    appointment = models.ForeignKey(
        Appointment,
        to_field="appointment_id",
        db_column="appointment_id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_orders",
    )

    customer = models.ForeignKey(
        Customer,
        to_field="customer_id",
        db_column="customer_id",
        on_delete=models.CASCADE,
        related_name="work_orders",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        to_field="vehicle_id",
        db_column="vehicle_id",
        on_delete=models.CASCADE,
        related_name="work_orders",
    )

    status = models.TextField(db_column="status")
    customer_symptoms = models.TextField(db_column="customer_symptoms", null=True, blank=True)
    diagnosis = models.TextField(db_column="diagnosis", null=True, blank=True)
    estimated_total = models.DecimalField(db_column="estimated_total", max_digits=12, decimal_places=2, null=True, blank=True)
    authorization_status = models.TextField(db_column="authorization_status")
    authorized_at = models.DateTimeField(db_column="authorized_at", null=True, blank=True)
    authorized_by = models.TextField(db_column="authorized_by", null=True, blank=True)
    assigned_mechanic_id = models.UUIDField(db_column="assigned_mechanic_id", null=True, blank=True)
    created_by = models.UUIDField(db_column="created_by", null=True, blank=True)
    opened_at = models.DateTimeField(db_column="opened_at")
    closed_at = models.DateTimeField(db_column="closed_at", null=True, blank=True)
    notes = models.TextField(db_column="notes", null=True, blank=True)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "work_orders"
        managed = False
        ordering = ["-opened_at"]


class WorkOrderService(models.Model):
    work_order_service_id = models.UUIDField(primary_key=True, db_column="work_order_service_id", default=uuid.uuid4, editable=False)

    work_order = models.ForeignKey(
        WorkOrder,
        to_field="work_order_id",
        db_column="work_order_id",
        on_delete=models.CASCADE,
        related_name="service_lines",
    )

    service = models.ForeignKey(
        Service,
        to_field="service_id",
        db_column="service_id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_order_services",
    )

    description = models.TextField(db_column="description", null=True, blank=True)
    qty = models.DecimalField(db_column="qty", max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(db_column="unit_price", max_digits=12, decimal_places=2)
    mechanic_id = models.UUIDField(db_column="mechanic_id", null=True, blank=True)
    status = models.TextField(db_column="status")
    started_at = models.DateTimeField(db_column="started_at", null=True, blank=True)
    completed_at = models.DateTimeField(db_column="completed_at", null=True, blank=True)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "work_order_services"
        managed = False
        ordering = ["-created_at"]


class WorkOrderProduct(models.Model):
    work_order_product_id = models.UUIDField(primary_key=True, db_column="work_order_product_id", default=uuid.uuid4, editable=False)

    work_order = models.ForeignKey(
        WorkOrder,
        to_field="work_order_id",
        db_column="work_order_id",
        on_delete=models.CASCADE,
        related_name="product_lines",
    )

    product = models.ForeignKey(
        Product,
        to_field="product_id",
        db_column="product_id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_order_products",
    )

    description = models.TextField(db_column="description", null=True, blank=True)
    qty = models.DecimalField(db_column="qty", max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(db_column="unit_price", max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "work_order_products"
        managed = False
        ordering = ["-created_at"]
