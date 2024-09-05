from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import User
from apps.utils.helper import get_config_value
from apps.utils.models import CreatedModifiedMixin


class Profile(CreatedModifiedMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    daily_votes = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.user.email}"

    def decrease_daily_votes(self, value: int = 1):
        self.daily_votes = (
            self.daily_votes - value if self.daily_votes > 0 else 0
        )
        self.save()

    def increase_daily_votes(self, value: int = 1):
        self.daily_votes = self.daily_votes + value
        self.save()

    def reset_daily_votes(self):
        self.daily_votes = get_config_value("USER_DAILY_VOTES")
        self.save()


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created: bool, **kwargs):
    """
    Create profile on when a user is created.
    """
    if created:
        Profile.objects.create(
            user=instance,
            daily_votes=get_config_value("USER_DAILY_VOTES")
        )
