from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentAdminViewSet,
    AppointmentCustomerViewSet,
    AppointmentSlotAdminViewSet,
    CustomerSlotViewSet,
)

router = DefaultRouter()
router.register(r"appointments", AppointmentAdminViewSet, basename="appointments")
router.register(r"customer-appointments", AppointmentCustomerViewSet, basename="customer-appointments")
router.register(r"appointment-slots", AppointmentSlotAdminViewSet, basename="appointment-slots")
router.register(r"customer-slots", CustomerSlotViewSet, basename="customer-slots")

urlpatterns = [path("", include(router.urls))]
