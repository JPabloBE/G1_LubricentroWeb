from rest_framework import generics
from rest_framework.exceptions import NotFound

from apps.catalog.permissions import IsAdminOrReadOnly, is_admin
from apps.customers.auth import CustomerJWTAuthentication
from apps.customers.permissions import IsAuthenticatedCustomer

from .models import Service, ServiceChangeLog
from .serializers import ServiceChangeLogSerializer, ServiceLiteSerializer, ServiceSerializer

TRACKED_FIELDS = ["name", "description", "base_price", "estimated_minutes", "requires_lift", "is_active"]


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.all()
        if is_admin(getattr(self.request, "user", None)):
            return qs
        return qs.filter(is_active=True)

    def perform_create(self, serializer):
        instance = serializer.save()
        user = getattr(self.request, "user", None)
        ServiceChangeLog.objects.create(
            service=instance,
            changed_by_id=user.pk if user and user.is_authenticated else None,
            change_type="create",
        )


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.all()
        if is_admin(getattr(self.request, "user", None)):
            return qs
        return qs.filter(is_active=True)

    def perform_update(self, serializer):
        instance = serializer.instance
        snapshot = {f: str(getattr(instance, f)) for f in TRACKED_FIELDS}
        updated = serializer.save()
        user = getattr(self.request, "user", None)
        user_id = user.pk if user and user.is_authenticated else None
        logs = []
        for field in TRACKED_FIELDS:
            old = snapshot[field]
            new = str(getattr(updated, field))
            if old != new:
                logs.append(
                    ServiceChangeLog(
                        service=updated,
                        changed_by_id=user_id,
                        change_type="update",
                        field_name=field,
                        old_value=old,
                        new_value=new,
                    )
                )
        if logs:
            ServiceChangeLog.objects.bulk_create(logs)


class ServiceChangeLogView(generics.ListAPIView):
    serializer_class = ServiceChangeLogSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        if not Service.objects.filter(pk=pk).exists():
            raise NotFound("Servicio no encontrado.")
        return ServiceChangeLog.objects.filter(service_id=pk)[:50]


class CustomerServiceListView(generics.ListAPIView):
    serializer_class = ServiceLiteSerializer
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticatedCustomer]

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("name")
