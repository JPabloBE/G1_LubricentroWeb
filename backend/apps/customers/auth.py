import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Customer


class CustomerJWTAuthentication(BaseAuthentication):
    """
    JWT SOLO para customers (token_type='customer').
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token inválido.")

        if payload.get("token_type") != "customer":
            return None

        customer_id = payload.get("customer_id")
        if not customer_id:
            raise AuthenticationFailed("Token inválido (sin customer_id).")

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            raise AuthenticationFailed("Cliente no existe.")

        if not customer.is_active:
            raise AuthenticationFailed("Cliente inactivo.")

        return (customer, token)
