from django.db import models
from django.db.models.functions import Lower

from apps.profiles.models import Profile
from apps.utils.models import CreatedModifiedMixin, NULLABLE


class Restaurant(CreatedModifiedMixin):
    name = models.CharField(max_length=128)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name="restaurants",
        **NULLABLE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_name_case_insensitive',
            )
        ]


class RestaurantVote(CreatedModifiedMixin):

    FIRST_VOTE = 1
    SECOND_VOTE = 0.5
    DEFAULT_VOTE = 0.25

    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name="votes",
        **NULLABLE
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    date = models.DateField()
    count = models.PositiveIntegerField(
        default=1,
        help_text="number of times the user voted for the restaurant on date"
    )
    total = models.FloatField(
        help_text="total sum of votes made by user for the restaurant on date"
    )

    def __str__(self) -> str:
        return f"{self.restaurant.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "profile", "restaurant"],
                name="unique_restaurant_vote"
            )
        ]
