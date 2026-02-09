from rest_framework import status

from .base_test import AuthenticationBaseTest


class TestUserSignup(AuthenticationBaseTest):
    def test_user_signup_succeeds(self):
        response = self.client.post(self.signup_url, self.valid_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), "Registration successfull")
        self.assertEqual(response.data.get("data", {}).get("email"), self.valid_user["email"])

    def test_user_signup_missing_fields_fails(self):
        response = self.client.post(self.signup_url, self.missing_fields_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_signup_invalid_password_fails(self):
        response = self.client.post(self.signup_url, self.invalid_password_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_user_signup_invalid_username_fails(self):
        response = self.client.post(self.signup_url, self.invalid_username_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_user_signup_duplicate_email_fails(self):
        self.create_user(email=self.valid_user["email"], username="dupe1")
        response = self.client.post(self.signup_url, self.valid_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_signup_duplicate_username_fails(self):
        self.create_user(email="unique@example.com", username=self.valid_user["username"])
        response = self.client.post(self.signup_url, self.valid_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
