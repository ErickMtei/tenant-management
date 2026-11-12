from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.response import Response

from .filters import PaymentFilter
from .models import Lease, Payment, Property, Tenant, Unit
from .serializers import (
    LeaseCreateSerializer,
    LeaseSerializer,
    PaymentSerializer,
    PropertySerializer,
    TenantSerializer,
    UnitSerializer,
)
from .services import add_payment, create_lease_with_payment


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
    """Leases can be listed, read and created. They are never edited or deleted by hand:
    end_date moves only when a payment is recorded."""

    queryset = Lease.objects.select_related('tenant', 'unit__property').order_by(
        '-start_date'
    )
    serializer_class = LeaseSerializer
    http_method_names = ['get', 'post', 'head', 'options']
    search_fields = ['tenant__full_name', 'unit__unit_number', 'unit__property__name']
    filterset_fields = ['is_active', 'tenant', 'unit', 'unit__property']

    def create(self, request, *args, **kwargs):
        serializer = LeaseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lease = create_lease_with_payment(**serializer.validated_data)
        return Response(LeaseSerializer(lease).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    """Payments are financial records: create and read only, never edit or delete."""

    queryset = Payment.objects.select_related(
        'lease__tenant', 'lease__unit__property'
    ).order_by('-payment_date', '-id')
    serializer_class = PaymentSerializer
    http_method_names = ['get', 'post', 'head', 'options']
    filterset_class = PaymentFilter
    search_fields = ['lease__tenant__full_name', 'reference']
    ordering_fields = ['payment_date', 'amount']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = add_payment(**serializer.validated_data)
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)