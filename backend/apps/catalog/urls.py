from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductChangeLogView,
    StockAdjustmentView,
    ProductMovementListView,
    GlobalMovementListView,
)

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category_detail"),

    # Products
    path("products/", ProductListCreateView.as_view(), name="product_list_create"),
    path("products/<uuid:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("products/<uuid:pk>/changelog/", ProductChangeLogView.as_view(), name="product_changelog"),
    path("products/<uuid:pk>/adjust-stock/", StockAdjustmentView.as_view(), name="product_adjust_stock"),
    path("products/<uuid:pk>/movements/", ProductMovementListView.as_view(), name="product_movements"),

    # Movimientos globales
    path("movements/", GlobalMovementListView.as_view(), name="global_movements"),
]
