from rest_framework import serializers
from app.api.organization.models import Property, Organization


class OrganizationSerializer(serializers.ModelSerializer):
      class Meta:
          model = Organization
          fields = ["id", "name", "slug", "is_active", "created_at", "updated_at"]
          read_only_fields = ["id", "created_at", "updated_at"]

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "organization", "name", "address", "deleted", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "deleted", "created_at", "updated_at"]

    def validate(self, attrs):
        view = self.context.get("view")
        org = None
        if view and hasattr(view, "get_organization"):
            org = view.get_organization()
        name = attrs.get("name")
        if org and name and Property.objects.filter(organization=org, name=name).exists():
            raise serializers.ValidationError(
                {"name": "A property with this name already exist in this organization"}
            )
        return attrs
    
