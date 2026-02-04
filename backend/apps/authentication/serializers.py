from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# -------------------------
# Me / list serializer (sin password)
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "user_type",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


# -------------------------
# Login SOLO staff/admin
# -------------------------
class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user_type = (getattr(self.user, "user_type", "") or "").strip().lower()
        allowed = bool(
            self.user.is_superuser
            or self.user.is_staff
            or user_type in ("admin", "staff")
        )
        if not allowed:
            raise serializers.ValidationError(
                {"detail": "Acceso denegado. Solo staff/admin pueden iniciar sesión."}
            )

        data["user"] = {
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "user_type": user_type,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
            "is_active": self.user.is_active,
        }
        return data


# -------------------------
# CRUD Staff/Admin - READ serializer
# -------------------------
class StaffUserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "user_type",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


# -------------------------
# CRUD Staff/Admin - CREATE (con password)
# -------------------------
class StaffUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    # permitimos elegir admin/staff pero el permiso lo controlamos en la vista (solo admin)
    user_type = serializers.ChoiceField(choices=["staff", "admin"], required=False, default="staff")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "user_type",
            "is_active",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})

        attrs["user_type"] = (attrs.get("user_type") or "staff").strip().lower()
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")

        user_type = (validated_data.get("user_type") or "staff").strip().lower()
        validated_data["user_type"] = user_type

        # Flags coherentes para dashboard
        if user_type == "admin":
            validated_data["is_staff"] = True
            validated_data["is_superuser"] = True
        else:
            validated_data["is_staff"] = True
            validated_data["is_superuser"] = False

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# -------------------------
# CRUD Staff/Admin - UPDATE (password opcional)
# -------------------------
class StaffUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user_type = serializers.ChoiceField(choices=["staff", "admin"], required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "user_type",
            "is_active",
            "password",
        ]

    def validate_user_type(self, value):
        return (value or "staff").strip().lower()

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if "user_type" in validated_data:
            ut = (validated_data.get("user_type") or "staff").strip().lower()
            instance.user_type = ut

            if ut == "admin":
                instance.is_staff = True
                instance.is_superuser = True
            else:
                instance.is_staff = True
                instance.is_superuser = False

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if password:
            validate_password(password)
            instance.set_password(password)

        instance.save()
        return instance
