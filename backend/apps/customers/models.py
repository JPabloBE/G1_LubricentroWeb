from django.db import models


class Customer(models.Model):
    customer_id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField(null=True, blank=True)

    full_name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    password_hash = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "customers"
