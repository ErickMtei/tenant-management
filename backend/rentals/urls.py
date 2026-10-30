from rest_framework.routers import DefaultRouter
from django.urls import path

from .reports import ArrearsReportView, SummaryReportView

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
urlpatterns = router.urls + [
    path('reports/arrears/', ArrearsReportView.as_view(), name='report-arrears'),
    path('reports/summary/', SummaryReportView.as_view(), name='report-summary'),
]