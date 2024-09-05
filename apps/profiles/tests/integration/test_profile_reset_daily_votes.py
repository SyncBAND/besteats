from django.core.management import call_command

from rest_framework import status

from apps.restaurants.models import RestaurantVote
from apps.restaurants.tests.factory.restaurant import RestaurantFactory
from apps.authentication.tests.factory.user import UserFactory
from apps.utils.helper import get_config_value, set_config_value
from apps.utils.tests.cases import BaseTestCase



class ProfileTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.RESTAURANT_URL = "/api/restaurants"
        self.user = UserFactory()
        self.restaurant_1 = RestaurantFactory(name="Maxines")
        self.force_login(self.user)

    def test_reset_daily_votes_for_all_profles(self):

        # users profile daily_votes are defaulted at 10 for now 
        self.assertEqual(self.user.profile.daily_votes, 10)

        response = self.api_client.post(
            f"{self.RESTAURANT_URL}/{self.restaurant_1.pk}/vote"
        )
        self.assertStatusCode(response, status.HTTP_200_OK)

        # user's daily_votes should decrease by 1
        self.assertEqual(self.user.profile.daily_votes, 9)
        
        call_command("reset_daily_votes_for_all_profles", verbosity=0)

        self.user.refresh_from_db()

        # the daily_votes should reset for all users 
        self.assertEqual(
            self.user.profile.daily_votes, get_config_value("USER_DAILY_VOTES")
        )
