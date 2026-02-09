import factory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app.api.organization.models import Organization, OrganizationMember, Property
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


class OrganizationBaseTest(APITestCase):
    def setUp(self):
        self.organizations_url = "/api/organizations/"

        self.org = OrganizationFactory()
        self.admin_user = UserFactory(username="admin_user", email="admin@example.com")
        self.member_user = UserFactory(username="member_user", email="member@example.com")
        self.other_user = UserFactory(username="other_user", email="other@example.com")

        OrganizationMemberFactory(organization=self.org, user=self.admin_user, role=Role.ADMIN)
        OrganizationMemberFactory(organization=self.org, user=self.member_user, role=Role.MEMBER)

        self.property = PropertyFactory(organization=self.org, name="Property A")

    def org_detail_url(self, org_id):
        return f"{self.organizations_url}{org_id}/"

    def properties_url(self, org_id):
        return f"/api/organizations/{org_id}/properties/"

    def property_detail_url(self, org_id, prop_id):
        return f"{self.properties_url(org_id)}{prop_id}/"

    @staticmethod
    def extract_results(response):
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data
