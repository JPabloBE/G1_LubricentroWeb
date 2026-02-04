from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    """
    Permite acceso solo a usuarios del negocio:
    - is_superuser OR is_staff OR user_type in ('admin','staff')
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_type = getattr(user, "user_type", "") or ""
        user_type = user_type.strip().lower()

        return bool(
            user.is_superuser
            or user.is_staff
            or user_type in ("admin", "staff")
        )


class IsAdminOnly(BasePermission):
    """
    Solo admin del negocio (o superuser).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_type = getattr(user, "user_type", "") or ""
        user_type = user_type.strip().lower()

        return bool(user.is_superuser or user_type == "admin")
