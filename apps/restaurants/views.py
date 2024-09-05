from django.db import transaction
from django.db.models import (
    Case, Count, F, FloatField, Q, Subquery, Sum, When
)
from django.utils.timezone import now

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.request import Request
from rest_framework.response import Response

from apps.restaurants.exceptions import (
    RestaurantUnvoteException,
    RestaurantVoteException
)
from apps.restaurants.models import Restaurant, RestaurantVote
from apps.restaurants.permissions import IsRestaurantCreatorOrAdmin
from apps.restaurants.serializers import (
    DateSerializer,
    RestaurantMostVotedSerializer,
    RestaurantSerializer,
    RestaurantVoteSerializer
)


@extend_schema(tags=["restaurants"])
class RestaurantViewSet(viewsets.ModelViewSet):

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly, IsRestaurantCreatorOrAdmin
    ]

    @extend_schema(
        responses=RestaurantVoteSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated]
    )
    @transaction.atomic
    def vote(self, request: Request, pk=None) -> Response:
        """
        Add vote
        """
        user_daily_votes = request.user.profile.daily_votes
        if user_daily_votes == 0:
            raise RestaurantVoteException()

        user_vote_details = {
            "profile": request.user.profile,
            "date": now().date(),
            "restaurant": self.get_object()
        }

        queryset = RestaurantVote.objects.filter(Q(**user_vote_details))
        vote = queryset.first()
        if vote:
            update_details = {
                "count": F("count") + 1,
                "total": Case(
                    When(count=0, then=F('total') + RestaurantVote.FIRST_VOTE),
                    When(count=1, then=F('total') + RestaurantVote.SECOND_VOTE),
                    default=F('total') + RestaurantVote.DEFAULT_VOTE,
                    output_field=FloatField()
                )
            }

            queryset.update(**update_details)
            # update vote with latest changes
            vote.refresh_from_db()
        else:
            vote = RestaurantVote.objects.create(
                **user_vote_details, total=RestaurantVote.FIRST_VOTE
            )

        request.user.profile.decrease_daily_votes()

        return Response(RestaurantVoteSerializer(vote).data)

    @extend_schema(
        responses=RestaurantVoteSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated]
    )
    @transaction.atomic
    def unvote(self, request: Request, pk=None) -> Response:
        """
        Remove/subtract vote
        """

        user_vote_details = {
            "profile": request.user.profile,
            "date": now().date(),
            "restaurant": self.get_object()
        }

        queryset = RestaurantVote.objects.filter(Q(**user_vote_details))
        vote = queryset.first()

        if not vote or vote.count == 0:
            raise RestaurantUnvoteException()

        update_details = {
            "count": F("count") - 1,
            "total": Case(
                When(count=2, then=F('total') - RestaurantVote.SECOND_VOTE),
                When(count__gt=2, then=F('total') - RestaurantVote.DEFAULT_VOTE),  # noqa: E501
                default=0,
                output_field=FloatField()
            )
        }

        queryset.update(**update_details)

        request.user.profile.increase_daily_votes()

        # update vote with latest changes
        vote.refresh_from_db()
        return Response(RestaurantVoteSerializer(vote).data)

    @extend_schema(
        responses=RestaurantMostVotedSerializer(many=True),
    )
    @action(
        detail=False,
        methods=["get"]
    )
    def most_voted(self, request):
        """
        Get most voted restaurant(s) for the today or passed date.
        """

        date_to_query = self.request.query_params.get("date", None)
        if date_to_query:
            serializer = DateSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            date_to_query = serializer.validated_data["date"]
        else:
            date_to_query = now().date()

        queryset = RestaurantVote.objects.filter(date=date_to_query)

        # Subquery that gets the most votes and voters for a restaurant
        most_voted_and_voters_count_subquery = (
            queryset.
            values('restaurant')  # group by restaurants
            .annotate(
                total_votes=Sum('total'),
                total_voter_count=Count('profile'),
                restaurant_id=F("restaurant_id"),
                restaurant_name=F("restaurant__name")
            )
        )

        most_voted_restaurants = (
            most_voted_and_voters_count_subquery.filter(
                total_voter_count=Subquery(
                    most_voted_and_voters_count_subquery
                    .order_by('-total_voter_count')
                    .values('total_voter_count')[:1]
                ),
                total_votes=Subquery(
                    most_voted_and_voters_count_subquery
                    .order_by('-total_votes')
                    .values('total_votes')[:1]
                )
            )
            .values(
                "restaurant_id",
                "restaurant_name",
                "total_votes",
                "total_voter_count"
            )
        )

        serializer = RestaurantMostVotedSerializer(
            most_voted_restaurants,
            many=True
        )
        return Response(serializer.data)


"""
created today?
- yes
-- second vote?
--- yes
---- add 0.5
--- no
---- add 0.25
- no
-- add first vote
"""
