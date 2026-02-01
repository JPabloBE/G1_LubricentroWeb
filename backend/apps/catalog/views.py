from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly


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


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.select_related("category").all()
