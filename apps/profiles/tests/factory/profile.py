import factory

from apps.profiles.models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.sequence(lambda n: f"user{n}")
    daily_votes = 10
