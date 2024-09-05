from typing import Dict


from django.test import TestCase, Client

from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.authentication.models import User


class BaseCase:
    def setUp(self):
        # API Client should be used for testing API endpoints
        self.api_client = APIClient()
        # http client should be used for testing regular webpages
        self.http_client = Client()

    def force_login(self, user: User):
        """
        Force log via the HTTP or API client as the user.
        """
        self.api_client.force_authenticate(user)
        self.http_client.force_login(user)

    def tearDown(self):
        super().setUp()


class BaseTestCase(BaseCase, TestCase):
    """
    Consists of tests functions that are used frequently
    """
    def assertStatusCode(
        self,
        response: Response,
        status_code: int
    ) -> Dict:
        """
        Assert the response code has the provided status code and
        return the JSON data for a one-liner if it's valid.
        """
        self.assertEqual(response.status_code, status_code)
        return response.json()
