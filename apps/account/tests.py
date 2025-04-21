from typing import Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

# Create your tests here.

User = get_user_model()


class UserCreationTestCase(TestCase):

    def setUp(self) -> None:
        User.objects.create(email="shyam6132@gmail.com", password="shyam", fullname='shyam')

    def test_create_user(self):
        user = User.objects.create_user(email="test@gmail.com", username='test', password="shyam", fullname='test')
        self.assertEqual(user.email, "test@gmail.com")
        self.assertTrue(user.is_active, True)
        self.assertFalse(user.is_staff, False)
        self.assertEqual(user.groups.name, 'Guest')

    def test_existing_user(self):
        with self.assertRaises(Exception) as context:
             User.objects.create(email="shyam6132@gmail.com", password="shyam", fullname='shyam')
        self.assertIn("unique constraint", str(context.exception).lower())

    def test_get_user(self):
        user = User.objects.get(email="shyam6132@gmail.com")
        self.assertEqual(user.email, "shyam6132@gmail.com")

    def test_worng_fullname(self):
        user = User.objects.create(email="shyam@gmail.com", fullname="2ada", password="Shyamkumar@1")
        self.assertEqual(user.email, "shyam@gmail.com")


class UserCreationViewTestCase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.createuser = reverse('account:create-user')

    def test_create_userView(self):
        user_data = {
            "email": "shyam@innowave.tech",
            "password": "Shyamkumar@5",
            "confirm_password": "Shyamkumar@5",
            "fullname": "shyam",
        }
        response = self.client.post(self.createuser, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_wrong_useremail(self):
        user_data = {
            "email": "shyam@shya.tech",
            "password": "Shyamkumar@5",
            "confirm_password": "Shyamkumar@5",
            "fullname": "shyam",
        }
        response = self.client.post(self.createuser, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_worng_password(self):
        user_data = {
            "email": "shyam@shya.tech",
            "password": "Shyamkuma",
            "confirm_password": "Shyamkumar@5",
            "fullname": "shyam",
        }
        response = self.client.post(self.createuser, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_wrong_confirm_password(self):
        user_data = {
            "email": "shyam@shya.tech",
            "password": "Shyamkumar@5",
            "confirm_password": "Shyamkum",
            "fullname": "shyam",
        }
        response = self.client.post(self.createuser, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_wrong_firstname(self):
        user_data = {
            "email": "shyam@shya.tech",
            "password": "Shyamkumar@5",
            "confirm_password": "Shyamkumar@5",
            "fullname": "shyam2",
        }
        response = self.client.post(self.createuser, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginTestCase(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.login = reverse('account:login')
        self.create = reverse('account:create-user')

    def test_login_user(self):
        user_data = {
            "email": "shyam@innowave.tech",
            "password": "Shyamkumar@5",
            "confirm_password": "Shyamkumar@5",
            "fullname": "shyam",
        }
        self.client.post(self.create, data=user_data)
        response = self.client.post(self.login, data={
            "email": "shyam@innowave.tech",
            "password": "Shyamkumar@1",
        }, content_type='JSON')
        self.assertEqual(User.objects.count(), 1)

    def test_wrong_login(self):
        response = self.client.post(self.login, data={
            "email": "shyam@gmail.com",
            "password": "shyam"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
