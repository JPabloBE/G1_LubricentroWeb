from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CashSessionViewSet, CashMovementViewSet

router = DefaultRouter()
router.register(r"cash/sessions",  CashSessionViewSet,  basename="cash-sessions")
router.register(r"cash/movements", CashMovementViewSet, basename="cash-movements")

urlpatterns = [path("", include(router.urls))]
