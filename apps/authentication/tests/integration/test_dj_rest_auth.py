from django.db.utils import IntegrityError

from allauth.account.models import EmailAddress
from rest_framework import status

from apps.utils.tests.cases import BaseTestCase
from apps.authentication.tests.factory.user import UserFactory
from django.contrib.auth import get_user_model


class TestDjRestAuthOverrides(BaseTestCase):
    """
    Test any dj-rest-auth functionality we're overriding here.
    """
    def test_create_user(self):

        response = self.api_client.post("/api/auth/registration/", {
            "email": "register@test.com",
            "username": "register@test.com",
            "password1": "power123!",
            "password2": "power123!",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_factory_create_integrity_error(self):

        with self.assertRaises(IntegrityError) as duplicate_error:
            # try to create the same account twice
            UserFactory(email="register@test.com")
            UserFactory(email="register@test.com")

        self.assertTrue(
            "duplicate key"
            in duplicate_error.exception.args[0]
        )

    def test_api_create_unique_constraint_error(self):

        # try to create the same account twice via the api
        response = self.api_client.post("/api/auth/registration/", {
            "email": "register@test.com",
            "username": "user1",
            "password1": "power123!",
            "password2": "power123!",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.api_client.post("/api/auth/registration/", {
            "email": "register@test.com",
            "username": "user2",
            "password1": "power123!",
            "password2": "power123!",
        })
        data = self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("violates unique constraint", data["detail"])

    def test_login_user(self):
        email = "register@test.com"
        password = "power123!"

        user = get_user_model().objects.create_user(
            username=email,
            email=email,
            password=password
        )
        response = self.api_client.post("/api/auth/login/", {
            "email": email,
            "password": password
        })

        data = self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(data["user"]["username"], user.username)
        self.assertIn("access", data)

    def test_createsuper_emailaddress_entry(self):
        email = "register@test.com"
        self.assertEqual(EmailAddress.objects.count(), 0)
        superuser = UserFactory(email=email, username=email, is_superuser=True)
        self.assertEqual(
            EmailAddress.objects.filter(email=superuser.email).count(), 1
        )
