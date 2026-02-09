from rest_framework import status

from .base_test import AuthenticationBaseTest


class TestUserLogin(AuthenticationBaseTest):
    def test_user_login_succeeds(self):
        user = self.create_user()
        response = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.valid_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("email"), user.email)
        self.assertIn("token", response.data)

    def test_login_missing_email_fails(self):
        response = self.client.post(self.login_url, {"password": self.valid_password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password_fails(self):
        response = self.client.post(self.login_url, {"email": "test@example.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials_fails(self):
        user = self.create_user()
        response = self.client.post(
            self.login_url,
            {"email": user.email, "password": "WrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
