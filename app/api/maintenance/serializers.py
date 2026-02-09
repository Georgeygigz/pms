from rest_framework import serializers
from app.api.maintenance.models import MaintenanceRequest, WorkOrder
from app.api.maintenance.transitions import MR_TRANSITIONS, WO_TRANSITIONS

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = [
            "id",
            "organization",
            "property",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_by", "updated_by", "created_at", "updated_at"]

    def validate_status(self, value):
        instance = self.instance
        if instance is None:
            return value
        
        allowed = MR_TRANSITIONS.get(instance.status, set())
        if value != instance.status and value not in allowed:
            raise serializers.ValidationError(
                 f"Invalid status transition: {instance.status}: {value}"
            )
        return value

class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "organization",
            "maintenance_request",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization", "maintenance_request", "created_at", "updated_at"]
    

    def validate_status(self, value):
        instance = self.instance
        if instance is None:
            return value
        
        allowed = WO_TRANSITIONS.get(instance.status, set())
        if value != instance.status and value not in allowed:
            raise serializers.ValidationError(
                f"Invalid status transition: {instance.status} -> {value}"
            )
        return value
