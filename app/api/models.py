import uuid
from django.core.exceptions import ValidationError
from django.db import models



class BaseModel(models.Model):
    """Common fields for all models defined here for reusability"""

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True 


class TenantManager(models.Manager):
    def for_org(self, organization):
        return self.filter(organization=organization)


class TenantModel(models.Model):
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    objects = TenantManager()

    class Meta:
        abstract = True
    

    def save(self, *args, **kwargs):
        if not self.organization_id:
            raise ValidationError("Organization must be set for tenant-aware models.")
        super().save(*args, **kwargs)