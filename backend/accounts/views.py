from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import RESOURCES


class MeView(APIView):
    """Tells React who is logged in and what they may do."""

    role_access = {'read': set(User.Role), 'write': set()}

    def get(self, request):
        user = request.user
        tenant = getattr(user, 'tenant_profile', None)
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'role': user.role,
                'tenant_id': tenant.id if tenant else None,
                'access': {
                    name: {
                        'read': user.role in rules['read'],
                        'write': user.role in rules['write'],
                    }
                    for name, rules in RESOURCES.items()
                },
            }
        )