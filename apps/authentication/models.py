from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.dispatch import receiver

from allauth.account.models import EmailAddress


class User(AbstractUser):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_case_insensitive',
            )
        ]


@receiver(post_save, sender=User)
def create_superuser_email_address(sender, instance: User, created, **kwargs):
    """
    Create superuser entry in EmailAddress table.
    """
    if created and instance.email and instance.is_superuser:
        EmailAddress.objects.get_or_create(
            user=instance,
            email=instance.email,
            defaults={'verified': instance.is_superuser, 'primary': True}
        )
