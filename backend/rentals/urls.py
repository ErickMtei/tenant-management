from rest_framework.routers import DefaultRouter

from .views import (
    LeaseViewSet,
    PaymentViewSet,
    PropertyViewSet,
    TenantViewSet,
    UnitViewSet,
)

router = DefaultRouter()
router.register('properties', PropertyViewSet)
router.register('units', UnitViewSet)
router.register('tenants', TenantViewSet)
router.register('leases', LeaseViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = router.urls
