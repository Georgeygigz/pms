from unittest.mock import patch

from rest_framework import status

from .base_test import MaintenanceBaseTest


class TestWorkOrders(MaintenanceBaseTest):
    @patch("app.api.maintenance.views.send_work_order_notification")
    def test_admin_can_create_work_order_and_notify(self, mock_task):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.work_orders_url(self.org.id, mr.id),
            {"title": "Fix leak", "description": "Check basement"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_task.delay.assert_called_once()

    def test_member_cannot_create_work_order(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post(
            self.work_orders_url(self.org.id, mr.id),
            {"title": "Fix leak", "description": "Check basement"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_list_work_orders(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        work_order = self.create_work_order(maintenance_request=mr)

        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.work_orders_url(self.org.id, mr.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertTrue(any(item["id"] == str(work_order.id) for item in results))

    def test_non_owner_cannot_view_work_order(self):
        mr = self.create_request(created_by=self.member_user, updated_by=self.member_user)
        work_order = self.create_work_order(maintenance_request=mr)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.work_order_detail_url(self.org.id, mr.id, work_order.id))
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_invalid_status_transition_rejected(self):
        work_order = self.create_work_order()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.work_order_detail_url(self.org.id, work_order.maintenance_request.id, work_order.id),
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_status_transition_succeeds(self):
        work_order = self.create_work_order()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.work_order_detail_url(self.org.id, work_order.maintenance_request.id, work_order.id),
            {"status": "accepted"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "accepted")
