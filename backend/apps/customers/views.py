import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.db import connection
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from apps.authentication.views import LoginRateThrottle
from .auth import CustomerJWTAuthentication
from .lockout import get_lockout_status, record_failure, clear_failures
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
@authentication_classes([])
def customer_register(request):
    throttle = LoginRateThrottle()
    if not throttle.allow_request(request, None):
        return Response({"detail": "Demasiados intentos. Intenta de nuevo en un minuto."}, status=429)
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = serializer.save()

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "token_type": "customer",
            "customer_id": str(customer.customer_id),
            "email": customer.email,
            "iat": now,
            "exp": now + timedelta(hours=12),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return Response(
        {
            "message": "Cliente registrado correctamente.",
            "access": token,
            "customer": {
                "customer_id": str(customer.customer_id),
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def customer_login(request):
    throttle = LoginRateThrottle()
    if not throttle.allow_request(request, None):
        return Response({"detail": "Demasiados intentos. Intenta de nuevo en un minuto."}, status=429)

    email = (request.data.get("email") or "").strip().lower()

    is_locked, remaining_mins = get_lockout_status(email)
    if is_locked:
        mins = f"{remaining_mins} minuto{'s' if remaining_mins != 1 else ''}"
        return Response(
            {"detail": f"Cuenta bloqueada temporalmente. Podés intentarlo de nuevo en {mins}."},
            status=429,
        )

    serializer = CustomerLoginSerializer(data=request.data)
    if not serializer.is_valid():
        if Customer.objects.filter(email__iexact=email, is_active=True).exists():
            record_failure(email)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    clear_failures(email)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([CustomerJWTAuthentication])
@permission_classes([IsAuthenticatedCustomer])
def customer_me(request):
    return Response(CustomerSerializer(request.user).data)


@api_view(["PATCH"])
@authentication_classes([CustomerJWTAuthentication])
@permission_classes([IsAuthenticatedCustomer])
def customer_update_me(request):
    customer = request.user
    data = request.data or {}

    sets, params = [], []

    if "full_name" in data:
        full_name = (data["full_name"] or "").strip()
        if not full_name:
            return Response({"detail": "El nombre no puede estar vacío."}, status=400)
        sets.append("full_name = %s")
        params.append(full_name)

    if "email" in data:
        email = (data["email"] or "").strip().lower()
        if not email:
            return Response({"detail": "El correo no puede estar vacío."}, status=400)
        conflict = Customer.objects.filter(email__iexact=email).exclude(customer_id=customer.customer_id).exists()
        if conflict:
            return Response({"detail": "Ese correo ya está registrado con otra cuenta."}, status=400)
        sets.append("email = %s")
        params.append(email)

    if "phone" in data:
        phone = (data["phone"] or "").strip()
        sets.append("phone = %s")
        params.append(phone or None)

    if not sets:
        return Response(CustomerSerializer(customer).data)

    sets.append("updated_at = now()")
    params.append(str(customer.customer_id))

    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE public.customers SET {', '.join(sets)} WHERE customer_id = %s",
            params,
        )

    customer.refresh_from_db()
    return Response(CustomerSerializer(customer).data)
