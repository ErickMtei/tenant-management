from django.db.models import Count
from rest_framework import viewsets

from .filters import PaymentFilter
from .models import Lease, Payment, Property, Tenant, Unit
from .serializers import (
    LeaseSerializer,
    PaymentSerializer,
    PropertySerializer,
    TenantSerializer,
    UnitSerializer,
)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.annotate(units_count=Count('units')).order_by('name')
    serializer_class = PropertySerializer
    search_fields = ['name', 'address', 'city']
    filterset_fields = ['city']


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('property').order_by(
        'property__name', 'unit_number'
    )
    serializer_class = UnitSerializer
    search_fields = ['unit_number', 'property__name']
    filterset_fields = ['status', 'property']
    ordering_fields = ['monthly_rent', 'unit_number']


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.order_by('full_name')
    serializer_class = TenantSerializer
    search_fields = ['full_name', 'phone_number', 'national_id']


class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.select_related('tenant', 'unit__property').order_by(
        '-start_date'
    )
    serializer_class = LeaseSerializer
    search_fields = ['tenant__full_name', 'unit__unit_number', 'unit__property__name']
    filterset_fields = ['is_active', 'tenant', 'unit', 'unit__property']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'lease__tenant', 'lease__unit__property'
    ).order_by('-payment_date')
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    search_fields = ['lease__tenant__full_name', 'reference']
    ordering_fields = ['payment_date', 'amount']