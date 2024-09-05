from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Apps
    path("", include("apps.authentication.urls")),
    path("", include("apps.restaurants.urls")),

    # Authentication
    path("api-auth/", include("rest_framework.urls")),

    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
