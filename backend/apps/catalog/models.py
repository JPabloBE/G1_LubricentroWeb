import uuid
from django.db import models


class ProductMovement(models.Model):
    MOVEMENT_TYPES = [
        ('sale', 'sale'),
        ('work_order', 'work_order'),
        ('work_order_refund', 'work_order_refund'),
        ('manual_adjustment', 'manual_adjustment'),
        ('purchase', 'purchase'),
        ('deactivation', 'deactivation'),
    ]

    movement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'Product',
        on_delete=models.DO_NOTHING,
        db_column='product_id',
        related_name='movements',
    )
    movement_type = models.TextField(choices=MOVEMENT_TYPES)
    qty_before = models.DecimalField(max_digits=12, decimal_places=2)
    qty_change = models.DecimalField(max_digits=12, decimal_places=2)
    qty_after = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(null=True, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    reference_type = models.TextField(null=True, blank=True)
    performed_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'product_movements'
        ordering = ['-created_at']


class ProductChangeLog(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        "Product",
        on_delete=models.DO_NOTHING,
        db_column="product_id",
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
        db_table = "product_change_log"
        ordering = ["-changed_at"]


class Category(models.Model):
    category_id = models.UUIDField(
        primary_key=True,
        db_column="category_id",
        default=uuid.uuid4,
        editable=False
    )
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "categories"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True,
        db_column="product_id",
        default=uuid.uuid4,
        editable=False
    )

    category = models.ForeignKey(
        Category,
        to_field="category_id",
        db_column="category_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    sku = models.TextField(blank=True, null=True, unique=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)

    image_url = models.TextField(blank=True, null=True, db_column="image_url")  # ✅ NUEVO

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    base_unit = models.CharField(max_length=50, default='unidad', db_column='base_unit')
    secondary_unit = models.CharField(max_length=50, null=True, blank=True, db_column='secondary_unit')
    secondary_unit_factor = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, db_column='secondary_unit_factor')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "products"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
