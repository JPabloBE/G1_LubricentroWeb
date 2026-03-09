from rest_framework import serializers
from .models import Appointment, AppointmentSlot


class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = [
            "slot_id",
            "start_at",
            "end_at",
            "capacity",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slot_id", "created_at", "updated_at"]


class AppointmentSlotCustomerSerializer(serializers.ModelSerializer):
    remaining_capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = ["slot_id", "start_at", "end_at", "remaining_capacity"]


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)

    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)
    vehicle_make = serializers.CharField(source="vehicle.make", read_only=True)
    vehicle_model = serializers.CharField(source="vehicle.model", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    slot_start = serializers.DateTimeField(source="slot.start_at", read_only=True)
    slot_end = serializers.DateTimeField(source="slot.end_at", read_only=True)

    work_order_id = serializers.SerializerMethodField()

    def get_work_order_id(self, obj):
        try:
            wo = obj.work_orders.first()
            return str(wo.work_order_id) if wo else None
        except Exception:
            return None

    class Meta:
        model = Appointment
        fields = [
            "appointment_id",
            "customer_id",
            "customer_name",
            "customer_email",
            "vehicle_id",
            "vehicle_plate",
            "vehicle_make",
            "vehicle_model",
            "service_id",
            "service_name",
            "slot_id",
            "slot_start",
            "slot_end",
            "scheduled_start",
            "scheduled_end",
            "requested_work",
            "status",
            "assigned_mechanic_id",
            "created_by",
            "notes",
            "admin_message",
            "progress_percent",
            "work_order_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["appointment_id", "created_at", "updated_at"]
