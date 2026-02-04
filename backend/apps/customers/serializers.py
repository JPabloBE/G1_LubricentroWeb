import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "customer_id",
            "full_name",
            "phone",
            "email",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = ["customer_id", "created_at", "updated_at", "last_login"]


class CustomerRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()
        full_name = validated_data["full_name"].strip()
        phone = validated_data.get("phone", "").strip()
        password = validated_data["password"]

        password_hash = make_password(password)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.customers
                  (full_name, email, phone, password_hash, is_active, created_at, updated_at, password_changed_at)
                values
                  (%s, %s, %s, %s, true, now(), now(), now())
                returning customer_id
                """,
                [full_name, email, phone, password_hash],
            )
            customer_id = cursor.fetchone()[0]

        return Customer.objects.get(customer_id=customer_id)


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        customer = Customer.objects.filter(email__iexact=email, is_active=True).first()
        if not customer or not customer.password_hash:
            raise serializers.ValidationError({"detail": "Credenciales inválidas."})

        if not check_password(password, customer.password_hash):
            raise serializers.ValidationError({"detail": "Credenciales inválidas."})

        with connection.cursor() as cursor:
            cursor.execute(
                "update public.customers set last_login = now(), updated_at = now() where customer_id = %s",
                [str(customer.customer_id)],
            )

        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=12)

        token = jwt.encode(
            {
                "token_type": "customer",
                "customer_id": str(customer.customer_id),
                "email": customer.email,
                "iat": now,
                "exp": exp,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return {
            "access": token,
            "customer": {
                "customer_id": str(customer.customer_id),
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
            },
        }
