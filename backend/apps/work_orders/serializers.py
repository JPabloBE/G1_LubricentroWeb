from decimal import Decimal
from rest_framework import serializers
from .models import WorkOrder, WorkOrderService, WorkOrderProduct

class WorkOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "work_order_id",
            "appointment_id",
            "customer_id",
            "customer_name",
            "customer_email",
            "vehicle_id",
            "vehicle_plate",
            "status",
            "customer_symptoms",
            "diagnosis",
            "estimated_total",
            "authorization_status",
            "authorized_at",
            "authorized_by",
            "assigned_mechanic_id",
            "created_by",
            "opened_at",
            "closed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["work_order_id", "created_at", "updated_at"]

class WorkOrderServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = WorkOrderService
        fields = [
            "work_order_service_id",
            "work_order_id",
            "service_id",
            "service_name",
            "description",
            "qty",
            "unit_price",
            "mechanic_id",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["work_order_service_id", "created_at", "updated_at"]


class WorkOrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = WorkOrderProduct
        fields = [
            "work_order_product_id",
            "work_order_id",
            "product_id",
            "product_name",
            "product_sku",
            "description",
            "qty",
            "unit_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["work_order_product_id", "created_at", "updated_at"]


class WorkOrderCustomerServiceLineSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderService
        fields = [
            "service_name",
            "description",
            "qty",
            "unit_price",
            "line_total",
            "status",
            "started_at",
            "completed_at",
        ]

    def get_line_total(self, obj):
        try:
            qty = Decimal(str(obj.qty or 0))
            price = Decimal(str(obj.unit_price or 0))
            return qty * price
        except Exception:
            return None


class WorkOrderCustomerProductLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderProduct
        fields = [
            "product_name",
            "product_sku",
            "description",
            "qty",
            "unit_price",
            "line_total",
        ]

    def get_line_total(self, obj):
        try:
            qty = Decimal(str(obj.qty or 0))
            price = Decimal(str(obj.unit_price or 0))
            return qty * price
        except Exception:
            return None


class WorkOrderCustomerSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)
    vehicle_make = serializers.CharField(source="vehicle.make", read_only=True)
    vehicle_model = serializers.CharField(source="vehicle.model", read_only=True)
    vehicle_year = serializers.CharField(source="vehicle.year", read_only=True)

    services = WorkOrderCustomerServiceLineSerializer(source="service_lines", many=True, read_only=True)
    products = WorkOrderCustomerProductLineSerializer(source="product_lines", many=True, read_only=True)

    services_total = serializers.SerializerMethodField()
    products_total = serializers.SerializerMethodField()
    computed_total = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            "vehicle_plate",
            "vehicle_make",
            "vehicle_model",
            "vehicle_year",
            "status",
            "authorization_status",
            "customer_symptoms",
            "diagnosis",
            "notes",
            "opened_at",
            "closed_at",
            "estimated_total",   
            "services",
            "products",
            "services_total",
            "products_total",
            "computed_total",
        ]

    def _sum_lines(self, lines):
        total = Decimal("0")
        for ln in lines:
            try:
                total += Decimal(str(ln.qty or 0)) * Decimal(str(ln.unit_price or 0))
            except Exception:
                continue
        return total

    def get_services_total(self, obj):
        return self._sum_lines(getattr(obj, "service_lines", []).all() if hasattr(obj, "service_lines") else [])

    def get_products_total(self, obj):
        return self._sum_lines(getattr(obj, "product_lines", []).all() if hasattr(obj, "product_lines") else [])

    def get_computed_total(self, obj):
        try:
            return self.get_services_total(obj) + self.get_products_total(obj)
        except Exception:
            return None
