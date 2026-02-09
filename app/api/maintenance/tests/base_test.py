import factory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app.api.organization.models import Organization, OrganizationMember, Property
from app.api.maintenance.models import MaintenanceRequest, WorkOrder
from app.api.constants import Role


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = "Test"
    last_name = "User"
    surname = "Tester"
    password = factory.PostGenerationMethodCall("set_password", "Pass1234")


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Org {n}")
    slug = factory.Sequence(lambda n: f"org-{n}")


class OrganizationMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationMember

    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserFactory)
    role = Role.MEMBER


class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    organization = factory.SubFactory(OrganizationFactory)
    name = "Building A"


class MaintenanceRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceRequest

    organization = factory.SelfAttribute("property.organization")
    property = factory.SubFactory(PropertyFactory)
    title = "Issue"
    description = "Desc"
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SelfAttribute("created_by")


class WorkOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkOrder

    organization = factory.SelfAttribute("maintenance_request.organization")
    maintenance_request = factory.SubFactory(MaintenanceRequestFactory)
    title = "Fix"


class MaintenanceBaseTest(APITestCase):
    def setUp(self):
        self.org = OrganizationFactory()
        self.other_org = OrganizationFactory()

        self.admin_user = UserFactory(username="admin_maint", email="admin.maint@example.com")
        self.member_user = UserFactory(username="member_maint", email="member.maint@example.com")
        self.other_user = UserFactory(username="other_maint", email="other.maint@example.com")

        OrganizationMemberFactory(organization=self.org, user=self.admin_user, role=Role.ADMIN)
        OrganizationMemberFactory(organization=self.org, user=self.member_user, role=Role.MEMBER)
        OrganizationMemberFactory(organization=self.org, user=self.other_user, role=Role.MEMBER)

        self.property = PropertyFactory(organization=self.org, name="Main Property")
        self.other_property = PropertyFactory(organization=self.other_org, name="Other Property")

    def maintenance_requests_url(self, org_id):
        return f"/api/organizations/{org_id}/maintenance-requests/"

    def maintenance_request_detail_url(self, org_id, mr_id):
        return f"{self.maintenance_requests_url(org_id)}{mr_id}/"

    def work_orders_url(self, org_id, mr_id):
        return f"/api/organizations/{org_id}/maintenance-requests/{mr_id}/work-orders/"

    def work_order_detail_url(self, org_id, mr_id, wo_id):
        return f"{self.work_orders_url(org_id, mr_id)}{wo_id}/"

    def create_request(self, **overrides):
        data = {
            "organization": self.org,
            "property": self.property,
            "created_by": self.member_user,
            "updated_by": self.member_user,
        }
        data.update(overrides)
        return MaintenanceRequestFactory(**data)

    def create_work_order(self, **overrides):
        mr = overrides.pop("maintenance_request", None)
        if mr is None:
            mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        data = {
            "organization": self.org,
            "maintenance_request": mr,
        }
        data.update(overrides)
        return WorkOrderFactory(**data)
