from django.db import IntegrityError

from rest_framework.exceptions import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, IntegrityError):
        response = Response(
            data={"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )

    return response
