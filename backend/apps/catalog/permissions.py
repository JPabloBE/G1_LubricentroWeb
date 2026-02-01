from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return (
        getattr(user, "user_type", None) == "admin"
        or getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
    )


class IsAdminOrReadOnly(BasePermission):
    """
    GET/HEAD/OPTIONS: permitido
    POST/PUT/PATCH/DELETE: solo admin
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_admin(request.user)
