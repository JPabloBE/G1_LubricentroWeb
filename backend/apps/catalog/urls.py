from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
)

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category_detail"),

    # Products
    path("products/", ProductListCreateView.as_view(), name="product_list_create"),
    path("products/<uuid:pk>/", ProductDetailView.as_view(), name="product_detail"),
]
