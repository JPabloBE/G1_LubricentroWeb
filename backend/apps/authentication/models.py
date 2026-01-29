"""
Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    """
    Usuario extendido para el sistema.
    Puede ser empleado (staff) o cliente.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Información adicional
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Tipo de usuario
    USER_TYPE_CHOICES = [
        ('staff', 'Staff/Empleado'),
        ('customer', 'Cliente'),
    ]
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"