from django.db import models
from django.conf import settings
from app.api.models import BaseModel, TenantModel
from app.api.constants import Role


class Organization(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly identifier")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class OrganizationMember(BaseModel, TenantModel):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_memberships")
    role = models.CharField(max_length=10, choices=Role.choices)

    class Meta:
        unique_together = ("organization", "user")
    
    def __str__(self):
        return f"{self.user.email} - {self.id} - {self.role}"


class Property(BaseModel, TenantModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"],
            name="unique_property_name_per_org"),
        ]
    

    def soft_delete(self):
        self.deleted = True
        self.save(update_fields=["deleted"])
    
    def __str__(self):
        return f"{self.name} - {self.id}"