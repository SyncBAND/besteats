from datetime import date
from unittest.mock import patch

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone

from freezegun import freeze_time
from rest_framework import status

from apps.restaurants.models import RestaurantVote
from apps.restaurants.tests.factory.restaurant import (
    RestaurantFactory,
    RestaurantVoteFactory
)
from apps.authentication.tests.factory.user import UserFactory
from apps.utils.helper import get_config_value, set_config_value
from apps.utils.tests.cases import BaseTestCase
from besteats.celery import app


URL = "/api/restaurants"


class RestaurantAnonymousTests(BaseTestCase):
    """
    Tests from an anonymous user to ensure the default
    permissions on these endpoints work as expected.
    """
    def test_list(self):
        response = self.api_client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = RestaurantFactory()
        response = self.api_client.get(f"{URL}/{obj.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        response = self.api_client.post(URL, {
            "name": "Castellos",
        })
        self.assertStatusCode(response, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        obj = RestaurantFactory()
        response = self.api_client.delete(f"{URL}/{obj.pk}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RestaurantAuthenticatedTests(BaseTestCase):
    """
    Tests from a logged in user who has permissions
    """
    def setUp(self):
        super().setUp()

        self.user = UserFactory()
        self.user_2 = UserFactory()
        self.force_login(self.user)

    def test_create(self):
        response = self.api_client.post(URL, {
            "name": "Castellos",
        })
        self.assertStatusCode(response, status.HTTP_201_CREATED)

    def test_update(self):
        # update resturant created by self.user
        obj = RestaurantFactory(profile=self.user.profile)
        response = self.api_client.patch(f"{URL}/{obj.pk}", {
            "name": "Castello's",
        })
        self.assertStatusCode(response, status.HTTP_200_OK)

    def test_update_not_allowed(self):
        # update resturant created by self.user which will raise an error
        self.force_login(self.user_2)

        obj = RestaurantFactory(profile=self.user.profile)
        response = self.api_client.patch(f"{URL}/{obj.pk}", {
            "name": "Castello",
        })
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)


class RestaurantTests(BaseTestCase):
    """
    Tests for the restaurant views
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()

        self.restaurant_1 = RestaurantFactory(name="Maxines")
        self.restaurant_2 = RestaurantFactory(name="Brunos")
        self.restaurant_3 = RestaurantFactory(name="Valaries")

        self.force_login(self.user)
    
        # Create the crontab schedule
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*'
        )
        
        # Create the periodic task
        self.periodic_task = PeriodicTask.objects.create(
            name='Reset User Daily Votes',
            task='apps.profiles.tasks.reset_daily_votes_for_all_profles',
            crontab=schedule,
            enabled=True
        )


    def test_user_vote(self):
        """
        add vote - testing increase restuarant by 1 for self.user's first
        vote and increase by 0.5 for second vote.
        """

        # users profile daily_votes are defaulted at 10 for now 
        self.assertEqual(self.user.profile.daily_votes, 10)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        self.assertStatusCode(response, status.HTTP_200_OK)

        # user's daily_votes should decrease by 1
        self.assertEqual(self.user.profile.daily_votes, 9)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # user's daily_votes should decrease by 1
        self.assertEqual(self.user.profile.daily_votes, 8)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # user's daily_votes should decrease by 1
        self.assertEqual(self.user.profile.daily_votes, 7)

        # ---

        # the remaining user votes should be 7, we'll loop through the rest
        # of the daily_votes until the user runs out of votes

        while self.user.profile.daily_votes > 0:
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        self.assertEqual(self.user.profile.daily_votes, 0)

        # throw an error that user has run out of votes
        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        data = self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have run out of votes", data["detail"])

        # reset daily_votes to 10
        set_config_value("USER_DAILY_VOTES", 10)
        self.user.profile.reset_daily_votes()
        self.assertEqual(
            self.user.profile.daily_votes,
            get_config_value("USER_DAILY_VOTES")
        )
        self.assertEqual(self.user.profile.daily_votes, 10)

    def test_restaurant_vote(self):
        """
        add vote - testing increase restuarant by 1 for self.user's first
        vote and increase by 0.5 for second vote.
        """

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        self.assertStatusCode(response, status.HTTP_200_OK)

        # self.restaurant_1 total votes should increse by 1
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # self.restaurant_1 total votes should increse by 0.5
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1.5)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # self.restaurant_1 total votes should increse by 0.25
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1.75)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # self.restaurant_1 total votes should continue incresing by 0.25
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 2)

        # ---

        # the remaining user votes should be 6, we'll loop through the rest
        # of the daily_votes until the user runs out of votes.

        while self.user.profile.daily_votes > 0:
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # the total votes a restaurant can get from a user is 3.5 votes
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 3.5)

        # try one more vote and restaurant_1 should still have 3.5 votes because
        # user has run out of votes
        self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 3.5)

    def test_user_unvote(self):
        """
        remove vote - testing increase restuarant by 1 for self.user's first
        vote and increase by 0.5 for second vote. Then we remove the votes
        starting with 0.5 then 1
        """

        # users profile daily_votes are defaulted at 10 for now 
        self.assertEqual(self.user.profile.daily_votes, 10)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

        # ---

        # self.restaurant_1 total votes should be at 1.75
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1.75)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/unvote")
        self.assertStatusCode(response, status.HTTP_200_OK)

        # user's daily_votes should increase by 1
        self.assertEqual(self.user.profile.daily_votes, 8)

        # self.restaurant_1 total votes should decrease by 0.25
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1.5)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/unvote")
        self.assertStatusCode(response, status.HTTP_200_OK)

        # user's daily_votes should increase by 1
        self.assertEqual(self.user.profile.daily_votes, 9)

        # self.restaurant_1 total votes should decrease by 0.5
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 1)

        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/unvote")
        self.assertStatusCode(response, status.HTTP_200_OK)

        # user's daily_votes should increase by 1
        self.assertEqual(self.user.profile.daily_votes, 10)

        # self.restaurant_1 total votes should decrease by 1
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 0)

        # return error because user cannot unvote any more
        response = self.api_client.post(f"{URL}/{self.restaurant_1.pk}/unvote")
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

        # user's daily_votes should still be 10
        self.assertEqual(self.user.profile.daily_votes, 10)

        # self.restaurant_1 total votes should still be 0
        rest_1_vote = RestaurantVote.objects.get(restaurant=self.restaurant_1)
        self.assertEqual(rest_1_vote.total, 0)

    def test_most_voted_restaurant(self):
        """
        scenario: self.restaurant_2 should win because it has 4 points and more unique voters
        ----------------------------------------------------------------------------------------------------------|
                          | self.user               | self.user_2             | self.user_3          | Total      |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_1 | 4 votes worth 2 points  | 4 votes worth 2 points  | 0                    | 4.0 points |
                          | (1 + 0.5 + 0.25 + 0.25) | (1 + 0.5 + 0.25 + 0.25) |                      |            |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_2 | 4 votes worth 2 points  | 1 vote worth 1 point    | 1 vote worth 1 point | 4.0 points |
                          | (1 + 0.5 + 0.25 + 0.25) | (1)                     | (1)                  |            |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_3 | 0                       | 0                       | 1 vote worth 1 point | 1.0 points |
                          |                         |                         | (1)                  |            |
        ----------------------------------------------------------------------------------------------------------|
        """

        # 4 votes by self.user for self.restaurant_1 and self.restaurant_2
        for _ in range(4):
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
            self.api_client.post(f"{URL}/{self.restaurant_2.pk}/vote")

        # login as self.user_2 and cast 4 votes by self.user_2
        # for self.restaurant_1 and 1 vote for self.restaurant_2
        self.force_login(self.user_2)
        for _ in range(4):
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
        self.api_client.post(f"{URL}/{self.restaurant_2.pk}/vote")

        # login as self.user_3 and cast 1 vote by self.user_3
        # for self.restaurant_2 and 1 vote for self.restaurant_3
        self.force_login(self.user_3)
        self.api_client.post(f"{URL}/{self.restaurant_2.pk}/vote")
        self.api_client.post(f"{URL}/{self.restaurant_3.pk}/vote")

        # check for the winner
        response = self.api_client.get(f"{URL}/most_voted")
        data = self.assertStatusCode(response, status.HTTP_200_OK)

        self.assertEqual(data[0]["restaurant_id"], self.restaurant_2.pk)
        self.assertEqual(data[0]["total_votes"], 4.0)
        self.assertEqual(data[0]["total_voter_count"], 3)

    def test_most_voted_restaurants(self):
        """
        scenario: self.restaurant_1 and self.restaurant_2 should win
        because they have the highest points and same unique voters
        ----------------------------------------------------------------------------------------------------------|
                          | self.user               | self.user_2             | self.user_3          | Total      |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_1 | 4 votes worth 2 points  | 4 votes worth 2 points  | 0                    | 4.0 points |
                          | (1 + 0.5 + 0.25 + 0.25) | (1 + 0.5 + 0.25 + 0.25) |                      |            |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_2 | 4 votes worth 2 points  | 4 vote worth 2 point    | 0                    | 4.0 points |
                          | (1 + 0.5 + 0.25 + 0.25) | (1)                     |                      |            |
        ----------------------------------------------------------------------------------------------------------|
        self.restaurant_3 | 0                       | 0                       | 1 vote worth 1 point | 1.0 points |
                          |                         |                         | (1)                  |            |
        ----------------------------------------------------------------------------------------------------------|
        """

        # 4 votes by self.user for self.restaurant_1 and self.restaurant_2
        for _ in range(4):
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
            self.api_client.post(f"{URL}/{self.restaurant_2.pk}/vote")

        # login as self.user_2 and cast
        # 4 votes by self.user for self.restaurant_1 and self.restaurant_2
        self.force_login(self.user_2)
        for _ in range(4):
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")
            self.api_client.post(f"{URL}/{self.restaurant_2.pk}/vote")

        # login as self.user_3 and cast 1 vote for self.restaurant_3
        self.force_login(self.user_3)
        self.api_client.post(f"{URL}/{self.restaurant_3.pk}/vote")

        # check for the winners
        response = self.api_client.get(f"{URL}/most_voted")
        data = self.assertStatusCode(response, status.HTTP_200_OK)

        self.assertEqual(data[0]["restaurant_id"], self.restaurant_1.pk)
        self.assertEqual(data[0]["total_votes"], 4.0)
        self.assertEqual(data[0]["total_voter_count"], 2)

        self.assertEqual(data[1]["restaurant_id"], self.restaurant_2.pk)
        self.assertEqual(data[1]["total_votes"], 4.0)
        self.assertEqual(data[1]["total_voter_count"], 2)

    def test_most_voted_restaurant_from_past_date(self):
        RestaurantVoteFactory(
            profile=self.user.profile,
            restaurant=self.restaurant_1,
            date=date(2024,2,1),
            total=15
        )
        RestaurantVoteFactory(
            profile=self.user.profile,
            restaurant=self.restaurant_2,
            date=date(2024,2,2),
            total=10
        )

        response = self.api_client.get(f"{URL}/most_voted?date=2024-02-01")
        data = self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(data[0]["total_votes"], 15)

        response = self.api_client.get(f"{URL}/most_voted?date=2024-02-02")
        data = self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(data[0]["total_votes"], 10)
        

    @patch("apps.profiles.tasks.reset_daily_votes_for_all_profles.apply_async")
    def test_reset_daily_votes_for_all_profles(self, mock_start_task):

        def check_and_run_task(current_time):
            if not self.is_task_due(current_time):
                return False
            
            set_config_value("USER_DAILY_VOTES", 10)
            task = app.tasks[self.periodic_task.task]
            task.run()
            return True

        # Test before midnight
        with freeze_time("2024-09-05 23:59:59"):
            # users profile daily_votes are defaulted at 10 for now 
            self.assertEqual(self.user.profile.daily_votes, 10)
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

            # user's daily_votes should decrease by 1
            self.assertEqual(self.user.profile.daily_votes, 9)
            self.api_client.post(f"{URL}/{self.restaurant_1.pk}/vote")

            # user's daily_votes should decrease by 1
            self.assertEqual(self.user.profile.daily_votes, 8)
        
        # Test at midnight
        with freeze_time("2024-09-06 00:00:00"):
            # Simulate Celery beat checking for due tasks
            check_and_run_task(timezone.now())
            self.user.refresh_from_db()
            self.assertEqual(self.user.profile.daily_votes, 10)

        # Test after midnight
        with freeze_time("2024-09-06 00:00:01"):
            check_and_run_task(timezone.now())

    def is_task_due(self, current_time):
        return (
            self.periodic_task.schedule.now() == current_time
            and self.periodic_task.enabled
        )