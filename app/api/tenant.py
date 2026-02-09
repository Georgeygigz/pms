from django.http import Http404
from app.api.organization.models import Organization

def get_current_org(request, org_id):
    try:
        return Organization.objects.get(id=org_id, is_active=True)
    except Organization.DoesNotExist:
        raise Http404("Organization not found or inactive")


