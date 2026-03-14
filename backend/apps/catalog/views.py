from rest_framework import generics
from rest_framework.exceptions import NotFound

from .models import Category, Product, ProductChangeLog
from .serializers import CategorySerializer, ProductChangeLogSerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly

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
        ProductChangeLog.objects.create(
            product=instance,
            changed_by_id=user.pk if user and user.is_authenticated else None,
            change_type="create",
        )


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.select_related("category").all()

    def perform_update(self, serializer):
        instance = serializer.instance
        snapshot = {f: str(getattr(instance, f)) for f in PRICE_FIELDS + ACTIVATION_FIELDS}
        updated = serializer.save()
        user = getattr(self.request, "user", None)
        user_id = user.pk if user and user.is_authenticated else None
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
