"""
URL Configuration for Lubricentro project
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/', include('apps.authentication.urls')),
    path('api/catalog/', include('apps.catalog.urls')),
]