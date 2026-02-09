import rules
from app.api.organization.models import OrganizationMember
from app.api.constants import Role

@rules.predicate
def is_org_member(user, organization):
    return OrganizationMember.objects.filter(user=user, organization=organization).exists()

@rules.predicate
def is_org_admin(user, organization):
    return OrganizationMember.objects.filter(user=user, organization=organization, role=Role.ADMIN).exists()

@rules.predicate
def is_request_owner(user, maintenance_request):
    return maintenance_request.created_by_id == user.id


@rules.predicate
def is_mr_org_admin(user, maintenance_request):
    return OrganizationMember.objects.filter(
        user=user,
        organization=maintenance_request.organization,
        role=Role.ADMIN,
    ).exists()


rules.add_rule("manage_properties", is_org_admin)
rules.add_rule("view_properties", is_org_member)
rules.add_rule("create_maintenance_request", is_org_member)
rules.add_rule("view_maintenance_request", is_mr_org_admin | is_request_owner)
rules.add_rule("update_maintenance_request", is_mr_org_admin | is_request_owner)
rules.add_rule("delete_maintenance_request", is_org_admin)
rules.add_rule("manage_work_orders", is_org_admin)
rules.add_rule("view_work_orders", is_mr_org_admin | is_request_owner)
