from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsStaffOrAdmin, IsAdminOnly
from .serializers import (
    UserSerializer,
    StaffTokenObtainPairSerializer,
    StaffUserAdminSerializer,
    StaffUserCreateSerializer,
    StaffUserUpdateSerializer,
)

User = get_user_model()


# -------------------------
# Login SOLO staff/admin
# -------------------------
class StaffLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = StaffTokenObtainPairSerializer


# -------------------------
# /me SOLO staff/admin
# -------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def logout(request):
    # El cliente borra tokens. (Si quisieras blacklist aquí se agrega.)
    return Response({"message": "Sesión cerrada."}, status=status.HTTP_200_OK)


# -------------------------
# CRUD Staff/Admin (módulo tipo otros)
# -------------------------
class StaffUserViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios del negocio.

    - LIST/RETRIEVE: staff/admin
    - CREATE/UPDATE/DELETE: SOLO admin (recomendado)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_queryset(self):
        return User.objects.filter(user_type__in=["admin", "staff"]).order_by("-date_joined")

    def get_serializer_class(self):
        if self.action == "create":
            return StaffUserCreateSerializer
        if self.action in ("update", "partial_update"):
            return StaffUserUpdateSerializer
        return StaffUserAdminSerializer

    def get_permissions(self):
        # Solo admin puede crear/editar/borrar
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOnly()]
        return [IsAuthenticated(), IsStaffOrAdmin()]
