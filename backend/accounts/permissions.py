from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User

R = User.Role
STAFF_READ = {R.ADMIN, R.OWNER, R.MANAGER, R.ACCOUNTANT}

# Single source of truth for who can do what
RESOURCES = {
    'properties': {'read': STAFF_READ, 'write': {R.ADMIN, R.MANAGER}},
    'units': {'read': STAFF_READ, 'write': {R.ADMIN, R.MANAGER}},
    'tenants': {'read': STAFF_READ | {R.TENANT}, 'write': {R.ADMIN, R.MANAGER}},
    'leases': {'read': STAFF_READ | {R.TENANT}, 'write': {R.ADMIN, R.MANAGER}},
    'payments': {
        'read': STAFF_READ | {R.TENANT},
        'write': {R.ADMIN, R.MANAGER, R.ACCOUNTANT},
    },
    'reports': {'read': STAFF_READ, 'write': set()},
}


def access_for(resource):
    return RESOURCES[resource]


class RolePermission(BasePermission):
    """Default deny: a view must declare role_access, or nobody gets in."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        access = getattr(view, 'role_access', None)
        if access is None:
            return False
        key = 'read' if request.method in SAFE_METHODS else 'write'
        return user.role in access[key]


class TenantScopedMixin:
    """Tenants only see rows that belong to them. Staff see everything.
    Set tenant_scope_field to the path that leads to the User, e.g. 'tenant__user'."""

    tenant_scope_field = None

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.TENANT:
            return queryset.filter(**{self.tenant_scope_field: user})
        return queryset