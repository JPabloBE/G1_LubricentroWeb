from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "estimated_minutes", "requires_lift", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active", "requires_lift")
