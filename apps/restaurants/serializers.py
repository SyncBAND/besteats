from rest_framework import serializers

from apps.profiles.serializers import ProfileSerializer
from apps.restaurants.models import Restaurant, RestaurantVote


class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Restaurant
        fields = ["id", "name"]

    def create(self, validated_data):
        validated_data["profile"] = self.context["request"].user.profile
        obj = super().create(validated_data)
        return obj


class RestaurantVoteSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    restaurant = RestaurantSerializer()

    class Meta:
        model = RestaurantVote
        fields = "__all__"

    read_only_fields = "__all__"


class RestaurantMostVotedSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField(read_only=True)
    restaurant_name = serializers.CharField(read_only=True)
    total_votes = serializers.FloatField(read_only=True)
    total_voter_count = serializers.IntegerField(read_only=True)


class DateSerializer(serializers.Serializer):
    date = serializers.DateField(format="%Y-%m-%d")
