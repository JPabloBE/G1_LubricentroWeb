from django.db import connection
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from .auth import CustomerJWTAuthentication
from .permissions import IsAuthenticatedCustomer
from .models import Customer
from .serializers import CustomerSerializer, CustomerRegisterSerializer, CustomerLoginSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    CRUD para dashboard (solo staff/admin).
    """
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        full_name = (data.get("full_name") or "").strip()
        email = data.get("email") or None
        phone = data.get("phone") or None
        notes = data.get("notes") or None
        is_active = bool(data.get("is_active", True))

        if not full_name:
            return Response({"detail": "full_name es requerido."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.customers
                  (full_name, email, phone, notes, is_active, created_at, updated_at)
                values
                  (%s, %s, %s, %s, %s, now(), now())
                returning customer_id
                """,
                [full_name, email, phone, notes, is_active],
            )
            customer_id = cursor.fetchone()[0]

        customer = Customer.objects.get(customer_id=customer_id)
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        customer = self.get_object()
        data = request.data or {}

        sets = []
        params = []

        if "full_name" in data:
            sets.append("full_name = %s")
            params.append((data.get("full_name") or "").strip())

        if "email" in data:
            email = data.get("email")
            sets.append("email = %s")
            params.append(email.strip() if email else None)

        if "phone" in data:
            phone = data.get("phone")
            sets.append("phone = %s")
            params.append(phone.strip() if phone else None)

        if "notes" in data:
            notes = data.get("notes")
            sets.append("notes = %s")
            params.append(notes.strip() if notes else None)

        if "is_active" in data:
            sets.append("is_active = %s")
            params.append(bool(data.get("is_active")))

        sets.append("updated_at = now()")
        params.append(str(customer.customer_id))

        with connection.cursor() as cursor:
            cursor.execute(
                f"update public.customers set {', '.join(sets)} where customer_id = %s",
                params,
            )

        customer.refresh_from_db()
        return Response(CustomerSerializer(customer).data, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_register(request):
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = serializer.save()
    return Response(
        {"message": "Cliente registrado correctamente.", "customer": CustomerSerializer(customer).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_login(request):
    serializer = CustomerLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([CustomerJWTAuthentication])
@permission_classes([IsAuthenticatedCustomer])
def customer_me(request):
    return Response(CustomerSerializer(request.user).data)
