import factory
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = "Test"
    last_name = "User"
    surname = "Tester"
    password = factory.PostGenerationMethodCall("set_password", "Pass1234")


class AuthenticationBaseTest(APITestCase):
    def setUp(self):
        self.signup_url = "/api/users/signup/"
        self.login_url = "/api/users/login/"
        self.valid_password = "Pass1234"
        self.valid_user = {
            "username": "jdoe",
            "email": "jane.doe@example.com",
            "password": self.valid_password,
        }
        self.invalid_password_user = {
            **self.valid_user,
            "email": "badpass@example.com",
            "username": "badpass",
            "password": "password",
        }
        self.invalid_username_user = {
            **self.valid_user,
            "email": "baduser@example.com",
            "username": "bad user",
        }
        self.missing_fields_user = {
            "username": "",
            "email": "",
            "password": "",
        }

    def create_user(self, **overrides):
        data = {
            "username": "loginuser",
            "email": "login@example.com",
            "first_name": "Log",
            "last_name": "In",
            "surname": "User",
        }
        data.update(overrides)
        user = UserFactory(**data)
        user.set_password(self.valid_password)
        user.save()
        return user
