import factory

from django.conf import settings

from apps.profiles.tests.factory.profile import ProfileFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.sequence(lambda n: f"user{n}")
    email = factory.sequence(lambda n: f"user{n}@myproject.nl")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def create_profile(self, create, extracted):
        if not create:
            return
        if extracted is None:
            # users profile daily_votes are defaulted TO 10 for TESTING
            self.profile.daily_votes = 10
            self.profile.save()
