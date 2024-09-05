from django.urls import path, include

from apps.restaurants import views
from apps.utils.urls import create_router


router = create_router()
router.register(r"restaurants", views.RestaurantViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
