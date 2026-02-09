from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from app.api.models import BaseModel, TenantModel
from app.api.organization.models import Property
from app.api.constants import Status, Priority

class MaintenanceRequest(BaseModel, TenantModel):
    
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="maintenance_requests")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="maintenance_requests_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="maintenance_requests_updated")

    def clean(self):
        if self.property.organization_id != self.organization_id:
            raise ValidationError("Property organization mismatch.")

class WorkOrder(BaseModel, TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
    
    maintenance_request = models.ForeignKey(
        MaintenanceRequest, on_delete=models.CASCADE, related_name="work_orders"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def clean(self):
        if self.maintenance_request.organization_id != self.organization_id:
            raise ValidationError("Maintenance request organization mismatch.")
    

class MaintenanceRequestStatusLog(BaseModel, TenantModel):
    maintenance_request = models.ForeignKey(
        MaintenanceRequest, on_delete=models.CASCADE, related_name="status_logs"
    )

    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)

    def clean(self):
        if self.maintenance_request.organization_id != self.organization_id:
            raise ValidationError("Maintenance request not associated with this organization")