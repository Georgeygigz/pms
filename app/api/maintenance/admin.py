from django.contrib import admin
from .models import MaintenanceRequest, MaintenanceRequestStatusLog, WorkOrder


admin.site.register(MaintenanceRequest)
admin.site.register(MaintenanceRequestStatusLog)
admin.site.register(WorkOrder)