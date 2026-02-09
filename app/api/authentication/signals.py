from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from app.api.authentication.models import User
from app.api.organization.models import OrganizationMember
from app.api.constants import Role

@receiver(pre_save, sender=User)
def capture_previous_org(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_org_id = None
        return
    previous = User.objects.filter(pk=instance.pk).only("organization_id").first()
    instance._previous_org_id = previous.organization_id if previous else None


@receiver(post_save, sender=User)
def create_default_membership(sender, instance, created, **kwargs):
    if not created:
        return
    
    with transaction.atomic():
        OrganizationMember.objects.get_or_create(
            organization=instance.organization,
            user=instance,
            role=Role.MEMBER,
        )


@receiver(post_save, sender=User)
def move_membership_on_org_change(sender, instance, created, **kwargs):
    if created:
        return
    previous_org_id = getattr(instance, "_previous_org_id", None)
    if not previous_org_id or previous_org_id == instance.organization_id:
        return

    with transaction.atomic():
        updated = OrganizationMember.objects.filter(
            user=instance,
            organization_id=previous_org_id,
        ).update(organization=instance.organization)
        if updated == 0:
            OrganizationMember.objects.get_or_create(
                organization=instance.organization,
                user=instance,
                role=Role.MEMBER,
            )
