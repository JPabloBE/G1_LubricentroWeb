from rest_framework import generics

from apps.catalog.permissions import IsAdminOrReadOnly, is_admin
from apps.customers.auth import CustomerJWTAuthentication
from apps.customers.permissions import IsAuthenticatedCustomer

from .models import Service
from .serializers import ServiceLiteSerializer, ServiceSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.all()
        if is_admin(getattr(self.request, "user", None)):
            return qs
        return qs.filter(is_active=True)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.all()
        if is_admin(getattr(self.request, "user", None)):
            return qs
        return qs.filter(is_active=True)


class CustomerServiceListView(generics.ListAPIView):
    serializer_class = ServiceLiteSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("name")
