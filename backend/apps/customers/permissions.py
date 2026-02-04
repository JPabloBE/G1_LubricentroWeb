from rest_framework.permissions import BasePermission
from .models import Customer


class IsAuthenticatedCustomer(BasePermission):
    def has_permission(self, request, view):
        return isinstance(getattr(request, "user", None), Customer)
