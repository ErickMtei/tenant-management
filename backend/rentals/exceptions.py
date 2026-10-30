from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Turn Django's ProtectedError into a clean 409 response."""
    if isinstance(exc, ProtectedError):
        return Response(
            {'detail': 'This record cannot be deleted because other records depend on it.'},
            status=status.HTTP_409_CONFLICT,
        )
    # Everything else is handled by DRF as usual
    return exception_handler(exc, context)