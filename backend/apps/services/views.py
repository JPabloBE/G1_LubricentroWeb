from rest_framework import generics

from apps.catalog.permissions import IsAdminOrReadOnly

from .models import Service
from .serializers import ServiceSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Service.objects.all()


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Service.objects.all()
