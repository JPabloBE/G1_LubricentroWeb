from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import StaffLoginView, me, logout, StaffUserViewSet

router = DefaultRouter()
router.register(r"staff-users", StaffUserViewSet, basename="staff-users")

urlpatterns = [
    path("login/", StaffLoginView.as_view(), name="staff_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", me, name="me"),
    path("logout/", logout, name="logout"),

    # ✅ Nuevo módulo CRUD
    path("", include(router.urls)),
]
