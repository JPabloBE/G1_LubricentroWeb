from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category_detail"),
]
