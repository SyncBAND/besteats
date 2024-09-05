from django.contrib import admin

from apps.restaurants.models import Restaurant, RestaurantVote


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "profile"]


@admin.register(RestaurantVote)
class RestaurantVoteAdmin(admin.ModelAdmin):
    list_display = ["profile", "restaurant", "date", "count", "total"]
    readonly_fields = ["id", "profile", "restaurant", "date", "count", "total"]
