from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OpenAppointmentsAdminViewSet,
    WorkOrderAdminViewSet,
    WorkOrderCustomerViewSet,
    WorkOrderProductAdminViewSet,
    WorkOrderServiceAdminViewSet,
)

router = DefaultRouter()
router.register(r"open-appointments", OpenAppointmentsAdminViewSet, basename="open-appointments")
router.register(r"work-orders", WorkOrderAdminViewSet, basename="work-orders")
router.register(r"customer-work-orders", WorkOrderCustomerViewSet, basename="customer-work-orders")
router.register(r"customer/work-orders", WorkOrderCustomerViewSet, basename="customer-work-orders-alias")
router.register(r"work-order-services", WorkOrderServiceAdminViewSet, basename="work-order-services")
router.register(r"work-order-products", WorkOrderProductAdminViewSet, basename="work-order-products")

urlpatterns = [
    path("", include(router.urls)),
]
