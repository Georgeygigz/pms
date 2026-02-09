from django.db.models.signals import pre_save
from django.dispatch import receiver
from app.api.maintenance.models import MaintenanceRequest, MaintenanceRequestStatusLog


@receiver(pre_save, sender=MaintenanceRequest)
def log_status_change(sender, instance, **kwargs):
    if instance._state.adding:
        return
    previous = MaintenanceRequest.objects.get(pk=instance.pk)
    if previous.status != instance.status:
        MaintenanceRequestStatusLog.objects.create(
            maintenance_request=instance,
            organization=instance.organization,
            old_status=previous.status,
            new_status=instance.status,
        )
    
    