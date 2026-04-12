from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.permissions import IsStaffOrAdmin
from apps.catalog.models import Product
from apps.catalog.stock import apply_stock_change
from apps.work_orders.models import WorkOrder
from .models import CashSession, CashMovement, CashClosing
from .serializers import (
    CashSessionSerializer,
    CashSessionListSerializer,
    CashMovementSerializer,
    CashClosingSerializer,
)


class CashSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get_serializer_class(self):
        if self.action == "list":
            return CashSessionListSerializer
        return CashSessionSerializer

    def get_queryset(self):
        return CashSession.objects.prefetch_related("movements", "closings").all()

    def create(self, request, *args, **kwargs):
        """Abrir caja — valida que no haya otra sesión abierta."""
        if CashSession.objects.filter(status="open").exists():
            return Response(
                {"detail": "Ya existe una caja abierta. Ciérrela antes de abrir una nueva."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data.copy()
        data["opened_by"] = str(request.user.id)
        serializer = CashSessionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """Retorna la sesión actualmente abierta, o 404."""
        try:
            session = CashSession.objects.prefetch_related("movements", "closings").get(status="open")
            return Response(CashSessionSerializer(session).data)
        except CashSession.DoesNotExist:
            return Response({"detail": "No hay caja abierta."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """Cierre normal: requiere actual_amount; motivo obligatorio si hay diferencia."""
        session = self.get_object()
        if session.status != "open":
            return Response({"detail": "La caja no está abierta."}, status=status.HTTP_400_BAD_REQUEST)

        actual_amount    = request.data.get("actual_amount")
        difference_reason = request.data.get("difference_reason", "")

        if actual_amount is None:
            return Response({"detail": "actual_amount es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        theoretical = _calculate_theoretical(session)
        diff = Decimal(str(actual_amount)) - theoretical

        if diff != 0 and not str(difference_reason).strip():
            return Response(
                {"detail": "difference_reason es obligatorio cuando hay diferencia entre el saldo teórico y el real."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending_wos = _pending_work_orders(session)
        now = timezone.now()

        CashClosing.objects.create(
            cash_session=session,
            closing_type="normal",
            theoretical_amount=theoretical,
            actual_amount=Decimal(str(actual_amount)),
            difference=diff,
            difference_reason=str(difference_reason).strip() or None,
            closed_by=request.user.id,
            closed_at=now,
            created_at=now,
        )
        session.status    = "closed"
        session.closed_by = request.user.id
        session.closed_at = now
        session.updated_at = now
        session.save(update_fields=["status", "closed_by", "closed_at", "updated_at"])

        session = CashSession.objects.prefetch_related("movements", "closings").get(pk=session.pk)
        resp = CashSessionSerializer(session).data
        resp["pending_work_orders_warned"] = pending_wos
        return Response(resp)

    @action(detail=True, methods=["post"], url_path="force-close")
    def force_close(self, request, pk=None):
        """Cierre forzado de emergencia — requiere audit_note obligatorio."""
        session = self.get_object()
        if session.status != "open":
            return Response({"detail": "La caja no está abierta."}, status=status.HTTP_400_BAD_REQUEST)

        audit_note = str(request.data.get("audit_note", "")).strip()
        if not audit_note:
            return Response(
                {"detail": "audit_note es requerido para realizar un cierre forzado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        theoretical = _calculate_theoretical(session)
        now = timezone.now()

        CashClosing.objects.create(
            cash_session=session,
            closing_type="forced",
            theoretical_amount=theoretical,
            actual_amount=theoretical,
            difference=Decimal("0.00"),
            audit_note=audit_note,
            closed_by=request.user.id,
            closed_at=now,
            created_at=now,
        )
        session.status    = "force_closed"
        session.closed_by = request.user.id
        session.closed_at = now
        session.updated_at = now
        session.save(update_fields=["status", "closed_by", "closed_at", "updated_at"])

        session = CashSession.objects.prefetch_related("movements", "closings").get(pk=session.pk)
        return Response(CashSessionSerializer(session).data)

    @action(detail=True, methods=["post"], url_path="intermediate-check")
    def intermediate_check(self, request, pk=None):
        """Verificación intermedia — genera snapshot sin cerrar la caja."""
        session = self.get_object()
        if session.status != "open":
            return Response({"detail": "La caja no está abierta."}, status=status.HTTP_400_BAD_REQUEST)

        actual_amount = request.data.get("actual_amount")
        if actual_amount is None:
            return Response({"detail": "actual_amount es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        theoretical = _calculate_theoretical(session)
        diff = Decimal(str(actual_amount)) - theoretical
        now  = timezone.now()

        closing = CashClosing.objects.create(
            cash_session=session,
            closing_type="intermediate",
            theoretical_amount=theoretical,
            actual_amount=Decimal(str(actual_amount)),
            difference=diff,
            difference_reason=str(request.data.get("difference_reason", "")).strip() or None,
            closed_by=request.user.id,
            closed_at=now,
            created_at=now,
        )
        return Response(CashClosingSerializer(closing).data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["get"], url_path="work-orders-summary")
    def work_orders_summary(self, request):
        """OTs abiertas con info de cliente y vehículo para el dropdown del frontend.
        Acepta ?work_order_id=<uuid> para incluir una OT específica aunque esté cerrada
        (útil al redirigir desde 'Cerrar y Cobrar')."""
        qs = WorkOrder.objects.select_related("customer", "vehicle").filter(
            status__in=["open", "in_progress", "ready"]
        ).order_by("-opened_at")[:100]

        def wo_to_dict(wo):
            customer_name = wo.customer.full_name if wo.customer else "—"
            vehicle_info = ""
            if wo.vehicle:
                parts = [wo.vehicle.make, wo.vehicle.model, wo.vehicle.plate]
                vehicle_info = " ".join(p for p in parts if p)
            opened = wo.opened_at.strftime("%d/%m/%Y") if wo.opened_at else ""
            return {
                "work_order_id":   str(wo.work_order_id),
                "display":         f"{customer_name} — {vehicle_info} — {opened}",
                "estimated_total": str(wo.estimated_total or "0.00"),
            }

        data = [wo_to_dict(wo) for wo in qs]

        include_id = request.query_params.get("work_order_id")
        if include_id:
            existing_ids = {d["work_order_id"] for d in data}
            if include_id not in existing_ids:
                try:
                    wo = WorkOrder.objects.select_related("customer", "vehicle").get(
                        work_order_id=include_id
                    )
                    data.insert(0, wo_to_dict(wo))
                except WorkOrder.DoesNotExist:
                    pass

        return Response(data)


class CashMovementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    serializer_class   = CashMovementSerializer

    def get_queryset(self):
        qs = CashMovement.objects.all()
        session_id = self.request.query_params.get("cash_session_id")
        if session_id:
            qs = qs.filter(cash_session_id=session_id)
        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        session_id = request.data.get("cash_session_id")
        try:
            CashSession.objects.get(pk=session_id, status="open")
        except CashSession.DoesNotExist:
            return Response(
                {"detail": "No se encontró una sesión de caja abierta con ese ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Descuento de inventario si es venta directa de producto
        product_id  = request.data.get("product_id")
        product_qty = request.data.get("product_qty")
        has_product = bool(product_id and product_qty)
        qty = None
        if has_product:
            try:
                product = Product.objects.get(pk=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response({"detail": "Producto no encontrado o inactivo."}, status=status.HTTP_400_BAD_REQUEST)
            qty = Decimal(str(product_qty))
            if qty <= 0:
                return Response({"detail": "La cantidad debe ser mayor a cero."}, status=status.HTTP_400_BAD_REQUEST)
            # Validación optimista de stock (apply_stock_change hará la definitiva con FOR UPDATE)
            if product.stock_qty < qty:
                return Response(
                    {"detail": f"Stock insuficiente. Disponible: {product.stock_qty}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user.id)

        if has_product:
            apply_stock_change(
                product_id=str(product_id),
                qty_change=-qty,
                movement_type="sale",
                performed_by=request.user.id,
                reason=request.data.get("description") or "Venta directa",
                reference_id=serializer.instance.cash_movement_id,
                reference_type="cash_movement",
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ── helpers ───────────────────────────────────────────────────────────────────

def _calculate_theoretical(session: CashSession) -> Decimal:
    """Saldo teórico = monto inicial + suma de todos los movimientos."""
    total = Decimal("0.00")
    for m in session.movements.all():
        total += m.amount
    return session.opening_amount + total


def _pending_work_orders(session: CashSession) -> list:
    """IDs de OTs vinculadas a esta sesión que aún no están completadas/cerradas."""
    wo_ids = list(
        session.movements
        .filter(work_order_id__isnull=False)
        .values_list("work_order_id", flat=True)
        .distinct()
    )
    if not wo_ids:
        return []
    pending = WorkOrder.objects.filter(
        work_order_id__in=wo_ids
    ).exclude(status__in=["completed", "closed", "cancelled"])
    return [str(wo.work_order_id) for wo in pending]
