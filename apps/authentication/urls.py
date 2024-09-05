from django.urls import include, path


urlpatterns = [
    path("api/auth/", include("dj_rest_auth.urls")),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls'))
]
