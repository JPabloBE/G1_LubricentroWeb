"""
URL Configuration for Lubricentro project
"""
from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import dashboard_metrics

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path("api/dashboard/metrics/", dashboard_metrics),
    
    # API Authentication
    path('api/auth/', include('apps.authentication.urls')),
    path('api/catalog/', include('apps.catalog.urls')),
    path('api/services/', include('apps.services.urls')),
    path("api/", include("apps.customers.urls")),
    path("api/", include("apps.vehicles.urls")),
    path("api/", include("apps.appointments.urls")),
    path("api/", include("apps.work_orders.urls")),
    path("api/", include("apps.cash_register.urls")),
    path("api/period-closures/", include("apps.period_closures.urls")),

]