from datetime import date, timedelta
import factory

from apps.profiles.tests.factory.profile import ProfileFactory
from apps.restaurants.models import Restaurant, RestaurantVote


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    name = factory.sequence(lambda n: f"restaurant {n}")


class RestaurantVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantVote

    profile = factory.SubFactory(ProfileFactory)
    restaurant = factory.SubFactory(RestaurantFactory)
    date = factory.sequence(lambda n: date(2024, 9, 1) + timedelta(days=n))
    total = 0
