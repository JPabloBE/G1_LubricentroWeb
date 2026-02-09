from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerVehicleViewSet, VehicleViewSet

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicles")
router.register(r"customer-vehicles", CustomerVehicleViewSet, basename="customer-vehicles")

urlpatterns = [path("", include(router.urls))]
