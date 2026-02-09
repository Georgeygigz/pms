from django.contrib import admin
from .models import Organization, OrganizationMember, Property

admin.site.register(Organization)
admin.site.register(OrganizationMember)
admin.site.register(Property)