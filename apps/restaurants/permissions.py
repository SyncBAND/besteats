from rest_framework import permissions

from apps.restaurants.models import Restaurant


class IsRestaurantCreatorOrAdmin(permissions.BasePermission):
    """
    Allows restaurant creators or staff to edit or delete it.
    """

    def has_object_permission(self, request, view, obj: Restaurant):
        # Grant users permission to allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Grant creators or staff permission to make changes
        return request.user.is_staff or obj.profile.user == request.user
