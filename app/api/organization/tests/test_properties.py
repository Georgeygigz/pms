from rest_framework import status

from .base_test import OrganizationBaseTest, PropertyFactory


class TestProperties(OrganizationBaseTest):
    def test_member_can_list_properties_succeeds(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.properties_url(self.org.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.extract_results(response)
        self.assertTrue(any(item["id"] == str(self.property.id) for item in results))

    def test_non_member_canot_list_properties(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.properties_url(self.org.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_property(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.properties_url(self.org.id),
            {"name": "Property B", "address": "123 Street"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("name"), "Property B")

    def test_member_cannot_create_property(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            self.properties_url(self.org.id),
            {"name": "Property C", "address": "456 Street"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_property_name_rejected(self):
        PropertyFactory(organization=self.org, name="Dup Name")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.properties_url(self.org.id),
            {"name": "Dup Name", "address": "789 Street"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_admin_can_soft_delete_property(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.property_detail_url(self.org.id, self.property.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.property.refresh_from_db()
        self.assertTrue(self.property.deleted)

        list_response = self.client.get(self.properties_url(self.org.id))
        results = self.extract_results(list_response)
        self.assertFalse(any(item["id"] == str(self.property.id) for item in results))

    def test_member_cannot_delete_property(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.delete(self.property_detail_url(self.org.id, self.property.id))
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
