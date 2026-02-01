import uuid
from django.db import models


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

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "products"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
