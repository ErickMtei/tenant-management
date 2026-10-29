from django.db.models import Count
from rest_framework import filters, viewsets

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
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address', 'city']


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('property').order_by('property__name', 'unit_number')
    serializer_class = UnitSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['unit_number', 'property__name']


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.order_by('full_name')
    serializer_class = TenantSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'phone_number', 'national_id']


class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.select_related('tenant', 'unit__property').order_by('-start_date')
    serializer_class = LeaseSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'lease__tenant', 'lease__unit__property'
    ).order_by('-payment_date')
    serializer_class = PaymentSerializer