from rest_framework import status

from .base_test import MaintenanceBaseTest


class TestMaintenanceRequests(MaintenanceBaseTest):
    def test_member_can_create_request(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            self.maintenance_requests_url(self.org.id),
            {"property": str(self.property.id), "title": "Leak", "priority": "low"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("title"), "Leak")

    def test_member_cannot_create_request_for_other_org_property(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            self.maintenance_requests_url(self.org.id),
            {"property": str(self.other_property.id), "title": "Leak", "priority": "low"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_view_own_request(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.maintenance_request_detail_url(self.org.id, mr.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_view_others_request(self):
        mr = self.create_request(created_by=self.other_user, updated_by=self.other_user)
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.maintenance_request_detail_url(self.org.id, mr.id))
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_admin_can_view_any_request(self):
        mr = self.create_request(created_by=self.other_user, updated_by=self.other_user)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.maintenance_request_detail_url(self.org.id, mr.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_delete_request(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.member_user)
        response = self.client.delete(self.maintenance_request_detail_url(self.org.id, mr.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_request(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.maintenance_request_detail_url(self.org.id, mr.id))
        self.assertIn(response.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

    def test_invalid_status_transition_rejected(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.member_user)
        response = self.client.patch(
            self.maintenance_request_detail_url(self.org.id, mr.id),
            {"status": "closed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
