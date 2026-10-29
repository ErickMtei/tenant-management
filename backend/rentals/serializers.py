from rest_framework import serializers

from .models import Lease, Payment, Property, Tenant, Unit


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


class LeaseSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    unit_label = serializers.CharField(source='unit.__str__', read_only=True)

    class Meta:
        model = Lease
        fields = [
            'id', 'tenant', 'tenant_name', 'unit', 'unit_label',
            'start_date', 'end_date', 'deposit_amount',
            'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        # On partial updates (PATCH), fall back to the existing values
        instance = self.instance
        unit = attrs.get('unit', getattr(instance, 'unit', None))
        start = attrs.get('start_date', getattr(instance, 'start_date', None))
        end = attrs.get('end_date', getattr(instance, 'end_date', None))
        is_active = attrs.get('is_active', getattr(instance, 'is_active', True))

        if end and start and end < start:
            raise serializers.ValidationError(
                {'end_date': 'End date cannot be before start date.'}
            )

        if is_active:
            others = Lease.objects.filter(unit=unit, is_active=True)
            if instance:
                others = others.exclude(pk=instance.pk)
            if others.exists():
                raise serializers.ValidationError(
                    {'unit': 'This unit already has an active lease.'}
                )

        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(
        source='lease.tenant.full_name', read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'lease', 'tenant_name', 'amount', 'payment_date',
            'period_month', 'method', 'reference', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate_period_month(self, value):
        if value.day != 1:
            raise serializers.ValidationError(
                'Period month must be the first day of the month.'
            )
        return value