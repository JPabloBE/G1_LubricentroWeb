from decimal import Decimal

from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, ProductChangeLog, ProductMovement
from .serializers import (
    CategorySerializer,
    ProductChangeLogSerializer,
    ProductMovementSerializer,
    ProductSerializer,
)
from .permissions import IsAdminOrReadOnly
from .stock import apply_stock_change, log_stock_movement

PRICE_FIELDS = ["unit_price", "cost"]
ACTIVATION_FIELDS = ["is_active"]


# --- Categories ---
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Category.objects.all()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()


# --- Products ---
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related("category").all()

    def perform_create(self, serializer):
        instance = serializer.save()
        user = getattr(self.request, "user", None)
        user_id = user.pk if user and user.is_authenticated else None
        ProductChangeLog.objects.create(
            product=instance,
            changed_by_id=user_id,
            change_type="create",
        )
        # Log stock inicial si es mayor a 0
        if instance.stock_qty and instance.stock_qty > 0:
            log_stock_movement(
                product_id=str(instance.pk),
                qty_before=Decimal("0"),
                qty_change=instance.stock_qty,
                qty_after=instance.stock_qty,
                movement_type="manual_adjustment",
                performed_by=user_id,
                reason="Stock inicial al crear producto",
            )


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.select_related("category").all()

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance
        old_stock = instance.stock_qty
        snapshot = {f: str(getattr(instance, f)) for f in PRICE_FIELDS + ACTIVATION_FIELDS}
        updated = serializer.save()
        user = getattr(self.request, "user", None)
        user_id = user.pk if user and user.is_authenticated else None

        # Log cambio de stock si lo hubo (ajuste manual vía edición de producto)
        new_stock = updated.stock_qty
        if new_stock != old_stock:
            qty_change = new_stock - old_stock
            log_stock_movement(
                product_id=str(updated.pk),
                qty_before=old_stock,
                qty_change=qty_change,
                qty_after=new_stock,
                movement_type="manual_adjustment",
                performed_by=user_id,
                reason="Edición directa del producto",
            )

        logs = []
        for field in PRICE_FIELDS:
            old, new = snapshot[field], str(getattr(updated, field))
            if old != new:
                logs.append(ProductChangeLog(
                    product=updated,
                    changed_by_id=user_id,
                    change_type="price_change",
                    field_name=field,
                    old_value=old,
                    new_value=new,
                ))
        old_active, new_active = snapshot["is_active"], str(getattr(updated, "is_active"))
        if old_active != new_active:
            change_type = "reactivated" if new_active == "True" else "deactivated"
            logs.append(ProductChangeLog(
                product=updated,
                changed_by_id=user_id,
                change_type=change_type,
                old_value=old_active,
                new_value=new_active,
            ))
            # Log de desactivación en bitácora de movimientos (snapshot del stock)
            if change_type == "deactivated":
                log_stock_movement(
                    product_id=str(updated.pk),
                    qty_before=new_stock,
                    qty_change=Decimal("0"),
                    qty_after=new_stock,
                    movement_type="deactivation",
                    performed_by=user_id,
                    reason="Producto desactivado",
                )
        if logs:
            ProductChangeLog.objects.bulk_create(logs)


class ProductChangeLogView(generics.ListAPIView):
    serializer_class = ProductChangeLogSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        if not Product.objects.filter(pk=pk).exists():
            raise NotFound("Producto no encontrado.")
        return ProductChangeLog.objects.filter(product_id=pk)[:50]


# --- Stock adjustment (ajuste manual) ---
class StockAdjustmentView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not product.is_active:
            return Response({"detail": "Producto inactivo. No se puede ajustar el stock."}, status=status.HTTP_400_BAD_REQUEST)

        qty_change_raw = request.data.get("qty_change")
        reason = str(request.data.get("reason") or "").strip()
        movement_type = request.data.get("movement_type", "manual_adjustment")

        if qty_change_raw is None:
            return Response({"detail": "qty_change es requerido."}, status=status.HTTP_400_BAD_REQUEST)
        if not reason:
            return Response({"detail": "reason es requerido."}, status=status.HTTP_400_BAD_REQUEST)
        if movement_type not in ("manual_adjustment", "purchase"):
            return Response({"detail": "movement_type debe ser 'manual_adjustment' o 'purchase'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qty_change = Decimal(str(qty_change_raw))
        except Exception:
            return Response({"detail": "qty_change inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if qty_change == 0:
            return Response({"detail": "qty_change no puede ser cero."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_stock = apply_stock_change(
                product_id=str(pk),
                qty_change=qty_change,
                movement_type=movement_type,
                performed_by=request.user.id,
                reason=reason,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "product_id": str(pk),
            "product_name": product.name,
            "base_unit": product.base_unit,
            "new_stock_qty": str(new_stock),
        }, status=status.HTTP_200_OK)


# --- Historial de movimientos por producto ---
class ProductMovementListView(generics.ListAPIView):
    serializer_class = ProductMovementSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        if not Product.objects.filter(pk=pk).exists():
            raise NotFound("Producto no encontrado.")
        qs = ProductMovement.objects.select_related("product", "product__category").filter(product_id=pk)
        movement_type = self.request.query_params.get("movement_type")
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        limit = min(int(self.request.query_params.get("limit", 50)), 200)
        return qs[:limit]


# --- Historial global de movimientos ---
class GlobalMovementListView(generics.ListAPIView):
    serializer_class = ProductMovementSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = ProductMovement.objects.select_related("product", "product__category").all()
        product_id = self.request.query_params.get("product_id")
        if product_id:
            qs = qs.filter(product_id=product_id)
        movement_type = self.request.query_params.get("movement_type")
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(product__category_id=category_id)
        date_from = self.request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        date_to = self.request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs[:200]
