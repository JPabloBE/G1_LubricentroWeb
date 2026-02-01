import uuid
from django.db import models


class Category(models.Model):
    category_id = models.UUIDField(
        primary_key=True,
        db_column="category_id",
        default=uuid.uuid4,  # OK aunque DB también tenga default
        editable=False
    )

    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)

    # IMPORTANTE: como la tabla es externa (Supabase), dejamos estos campos
    # sin auto_now/auto_now_add para no pelear con la DB.
    created_at = models.DateTimeField(db_column="created_at")
    updated_at = models.DateTimeField(db_column="updated_at")

    class Meta:
        db_table = "categories"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
