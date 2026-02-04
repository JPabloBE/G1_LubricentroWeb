from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, customer_register, customer_login, customer_me

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customers")

urlpatterns = [
    # CRUD dashboard staff/admin
    path("", include(router.urls)),

    # Auth customers
    path("customer-auth/register/", customer_register, name="customer_register"),
    path("customer-auth/login/", customer_login, name="customer_login"),
    path("customer-auth/me/", customer_me, name="customer_me"),
]
