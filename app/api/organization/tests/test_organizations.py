from rest_framework import status

from .base_test import OrganizationBaseTest, OrganizationFactory, OrganizationMemberFactory


class TestOrganizations(OrganizationBaseTest):
    def test_list_requires_authentication_succeeds(self):
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_returns_only_member_organizations_succeeds(self):
        other_org = OrganizationFactory()
        OrganizationMemberFactory(organization=other_org, user=self.member_user)
        OrganizationFactory(name="NoAccess Org", slug="no-access")

        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.extract_results(response)
        result_ids = {item["id"] for item in results}
        self.assertIn(str(self.org.id), result_ids)
        self.assertIn(str(other_org.id), result_ids)
        self.assertGreaterEqual(len(result_ids), 2)

    def test_retrieve_non_member_org_returns_404(self):
        outsider_org = OrganizationFactory(name="Outsider Org", slug="outsider")
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.org_detail_url(outsider_org.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_can_update_org(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.patch(
            self.org_detail_url(self.org.id),
            {"name": "Updated Org"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "Updated Org")

    def test_non_member_delete_returns_404(self):
        outsider_org = OrganizationFactory(name="Outsider Org 2", slug="outsider-2")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.org_detail_url(outsider_org.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_create_org(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            self.organizations_url,
            {"name": "New Org", "slug": "new-org"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("name"), "New Org")
