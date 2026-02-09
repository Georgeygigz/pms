from django.db import IntegrityError
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import rules

from app.api.organization.models import Property
from app.api.organization.serializers import PropertySerializer
from app.api.viewmixins import OrganizationScopedMixin
from app.api.organization.models import Organization
from app.api.organization.serializers import OrganizationSerializer

class PropertyViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("\n HERE>>>>>>>>>>>>>>>")
        print(self.request.user.__dict__)
        print(" Close>>>>>>>>>>>>>>>\n")

        if getattr(self, "swagger_fake_view", False):
            return Property.objects.none()
        org = self.get_organization()
        self.ensure_membership(org)

        qs = Property.objects.filter(organization=org, deleted=False)
        if self.request.method in ["GET"]:
            return qs
        
        if rules.test_rule("manage_properties", self.request.user, org):
            return qs
        
        return Property.objects.none()
    

    def perform_create(self, serializer):
        org = self.get_organization()
        self.ensure_membership(org)
        if not rules.test_rule("manage_properties", self.request.user, org):
            raise PermissionDenied("Only admins can manage properties.")
        try:
            serializer.save(organization=org)
        except IntegrityError:
            raise serializers.ValidationError(
                {"name": "A property with this name already exists in this organization."}
            )

    
    def perform_destroy(self, instance):
        org = self.get_organization()
        if not rules.test_rule("manage_properties", self.request.user, org):
            raise PermissionDenied("Only admins can manage properties.")
        instance.soft_delete()


class OrganizationViewSet(viewsets.ModelViewSet):
      serializer_class = OrganizationSerializer
      permission_classes = [IsAuthenticated]

      def get_queryset(self):
        print("\n HERE>>>>>>>>>>>>>>>")
        print(self.request.user.__dict__)
        print(" Close>>>>>>>>>>>>>>>\n")
        if getattr(self, "swagger_fake_view", False):
            return Organization.objects.none()
        return Organization.objects.filter(organizationmembers__user=self.request.user).distinct()
