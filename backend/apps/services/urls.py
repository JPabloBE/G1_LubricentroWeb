from django.urls import path

from .views import CustomerServiceListView, ServiceChangeLogView, ServiceDetailView, ServiceListCreateView

urlpatterns = [
    path("", ServiceListCreateView.as_view(), name="service_list_create"),
    path("customer/", CustomerServiceListView.as_view(), name="customer_service_list"),
    path("<uuid:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path("<uuid:pk>/changelog/", ServiceChangeLogView.as_view(), name="service_changelog"),
]
