from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .permissions import IsStaffOrAdmin, IsAdminOnly
from .serializers import (
    UserSerializer,
    StaffTokenObtainPairSerializer,
    StaffUserAdminSerializer,
    StaffUserCreateSerializer,
    StaffUserUpdateSerializer,
)

User = get_user_model()


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# -------------------------
# Login SOLO staff/admin
# -------------------------
class StaffLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
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
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            RefreshToken(refresh_token).blacklist()
    except TokenError:
        pass  # Ya en blacklist o token inválido — no es un error
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


# ── Dashboard Metrics ──────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def dashboard_metrics(request):
    """
    Devuelve 4 grupos de métricas en una sola llamada para el dashboard principal.
    Acepta ?month=YYYY-MM para filtrar gráficos por un mes específico.
    """
    from datetime import date, timedelta
    from django.db import connection

    today = date.today()
    month_start = today.replace(day=1)

    # Filtro de mes opcional para los gráficos
    month_param = request.query_params.get("month")  # "YYYY-MM"
    filter_start = filter_end = None
    if month_param:
        try:
            y, m = map(int, month_param.split("-"))
            filter_start = date(y, m, 1)
            filter_end = date(y + (m // 12), (m % 12) + 1, 1) - timedelta(days=1)
        except (ValueError, TypeError):
            pass

    MONTH_NAMES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    with connection.cursor() as cursor:
        # 1. Citas por estado
        cursor.execute(
            "SELECT status, COUNT(*) FROM public.appointments GROUP BY status"
        )
        appointments_by_status = {r[0]: int(r[1]) for r in cursor.fetchall()}

        # 2. OTs por estado (filtrado por mes si se indica)
        if filter_start:
            cursor.execute(
                "SELECT status, COUNT(*) FROM public.work_orders WHERE opened_at::date >= %s AND opened_at::date <= %s GROUP BY status",
                [filter_start, filter_end],
            )
        else:
            cursor.execute(
                "SELECT status, COUNT(*) FROM public.work_orders GROUP BY status"
            )
        work_orders_by_status = {r[0]: int(r[1]) for r in cursor.fetchall()}

        # 3. Ingresos: diarios si hay filtro de mes, mensuales (12 meses) si no
        if filter_start:
            cursor.execute(
                """
                SELECT cm.created_at::date AS day, COALESCE(SUM(cm.amount), 0)
                FROM django_app.cash_movements cm
                JOIN django_app.cash_sessions cs ON cs.cash_session_id = cm.cash_session_id
                WHERE cm.created_at::date >= %s AND cm.created_at::date <= %s AND cm.amount > 0
                GROUP BY cm.created_at::date
                ORDER BY day
                """,
                [filter_start, filter_end],
            )
            monthly_income = [{"month": str(r[0]), "amount": float(r[1])} for r in cursor.fetchall()]
        else:
            cursor.execute(
                """
                SELECT DATE_TRUNC('month', cm.created_at)::date AS month, COALESCE(SUM(cm.amount), 0)
                FROM django_app.cash_movements cm
                JOIN django_app.cash_sessions cs ON cs.cash_session_id = cm.cash_session_id
                WHERE cm.created_at::date >= (DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months')::date
                  AND cm.amount > 0
                GROUP BY DATE_TRUNC('month', cm.created_at)
                ORDER BY month
                """,
            )
            monthly_income = [{"month": str(r[0]), "amount": float(r[1])} for r in cursor.fetchall()]

        # 4. Movimientos por tipo en el mes actual
        cursor.execute(
            """
            SELECT cm.movement_type, COALESCE(SUM(cm.amount), 0)
            FROM django_app.cash_movements cm
            JOIN django_app.cash_sessions cs ON cs.cash_session_id = cm.cash_session_id
            WHERE cs.opened_at::date >= %s
            GROUP BY cm.movement_type
            """,
            [month_start],
        )
        movements_by_type = {r[0]: float(r[1]) for r in cursor.fetchall()}

        # 5. OTs cerradas este mes
        cursor.execute(
            "SELECT COUNT(*) FROM public.work_orders WHERE status = 'closed' AND closed_at::date >= %s",
            [month_start],
        )
        wo_closed_month = int(cursor.fetchone()[0])

        # 6. ¿Hay sesión de caja abierta?
        cursor.execute(
            "SELECT COUNT(*) FROM django_app.cash_sessions WHERE status = 'open'"
        )
        cash_session_open = int(cursor.fetchone()[0]) > 0

    if filter_start:
        income_label = f"Ingresos diarios — {MONTH_NAMES[filter_start.month]} {filter_start.year}"
        wo_label     = f"OTs abiertas en {MONTH_NAMES[filter_start.month]} {filter_start.year}"
    else:
        income_label = "Ingresos mensuales — últimos 12 meses"
        wo_label     = "Pipeline del taller"

    return Response(
        {
            "appointments_by_status": appointments_by_status,
            "work_orders_by_status": work_orders_by_status,
            "monthly_income": monthly_income,
            "movements_by_type": movements_by_type,
            "wo_closed_month": wo_closed_month,
            "cash_session_open": cash_session_open,
            "income_label": income_label,
            "wo_label": wo_label,
            "is_filtered": bool(filter_start),
            "month_label": MONTH_NAMES[month_start.month] + " " + str(month_start.year),
        }
    )
