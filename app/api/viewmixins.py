from rest_framework.exceptions import PermissionDenied
from app.api.organization.models import OrganizationMember
from app.api.tenant import get_current_org
from app.api.constants import Role

class OrganizationScopedMixin:
    organization_url_kwarg = "org_pk"

    def get_organization(self):
        org_id = self.kwargs[self.organization_url_kwarg]
        return get_current_org(self.request, org_id)
    

    def ensure_membership(self, organization):
        if not OrganizationMember.objects.filter(
            user=self.request.user,organization=organization).exists():
            raise PermissionDenied("Not a member of this organization.")
    
    def is_org_admin(self, organization):
        return OrganizationMember.objects.filter(
            user=self.request.user,
            organization=organization,
            role=Role.ADMIN,
        ).exists()
    