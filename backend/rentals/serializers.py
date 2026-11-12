from rest_framework import serializers
from .models import Lease, Payment, Property, Tenant, Unit
from django.utils import timezone


class PropertySerializer(serializers.ModelSerializer):
    # Filled by annotate() in the viewset, so no extra query per row
    units_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'city', 'created_at', 'units_count']
        read_only_fields = ['created_at']


class UnitSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'property', 'property_name',
            'unit_number', 'monthly_rent', 'status',
        ]


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'id', 'full_name', 'phone_number',
            'email', 'national_id', 'created_at',
        ]
        read_only_fields = ['created_at']


from django.utils import timezone

# ... imports zilizopo juu, ongeza mstari huo ...


class LeaseSerializer(serializers.ModelSerializer):
    """Read-only view of a lease. Leases are created through LeaseCreateSerializer."""

    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    unit_label = serializers.CharField(source='unit.__str__', read_only=True)

    class Meta:
        model = Lease
        fields = [
            'id', 'tenant', 'tenant_name', 'unit', 'unit_label',
            'start_date', 'end_date', 'is_active', 'created_at',
        ]
        read_only_fields = fields


class LeaseCreateSerializer(serializers.Serializer):
    """Input for creating a lease together with its first payment."""

    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all())
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    start_date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_date = serializers.DateField(default=timezone.localdate)
    method = serializers.ChoiceField(choices=Payment.Method.choices, default=Payment.Method.CASH)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(
        source='lease.tenant.full_name', read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'lease', 'tenant_name', 'amount', 'monthly_rent', 'months',
            'payment_date', 'method', 'reference', 'created_at',
        ]
        # monthly_rent and months are calculated by the system (step 6.2)
        read_only_fields = ['monthly_rent', 'months', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value