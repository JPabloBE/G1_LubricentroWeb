from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PeriodClosureViewSet

router = DefaultRouter()
router.register(r"", PeriodClosureViewSet, basename="period-closures")

urlpatterns = [path("", include(router.urls))]
