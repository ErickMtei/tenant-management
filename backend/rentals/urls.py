from django.urls import path
from rest_framework.routers import DefaultRouter

from .reports import ExpiringLeasesReportView, SummaryReportView
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

urlpatterns = router.urls + [
    path('reports/expiring/', ExpiringLeasesReportView.as_view(), name='report-expiring'),
    path('reports/summary/', SummaryReportView.as_view(), name='report-summary'),
]