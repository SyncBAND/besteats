from django.conf import settings

from rest_framework import routers
from rest_framework.routers import BaseRouter


def create_router() -> BaseRouter:
    # Only use the DefaultRouter if we have browseable enabled
    RouterClass = (
        routers.DefaultRouter
        if settings.ENABLE_BROWSEABLE else
        routers.SimpleRouter
    )
    return RouterClass(trailing_slash=False)
