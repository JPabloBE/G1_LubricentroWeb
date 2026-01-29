"""
Authentication URL patterns
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    get_current_user,
    logout,
)

urlpatterns = [
    # Registro
    path('register/', RegisterView.as_view(), name='register'),
    
    # Login (JWT)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuario actual
    path('me/', get_current_user, name='current_user'),
    
    # Logout
    path('logout/', logout, name='logout'),
]