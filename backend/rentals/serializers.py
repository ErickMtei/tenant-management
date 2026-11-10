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
            'start_date', 'end_date', 'is_active', 'created_at',
        ]
        # end_date is calculated by the system from payments (step 6.2)
        read_only_fields = ['end_date', 'created_at']

    def validate(self, attrs):
        # On partial updates (PATCH), fall back to the existing values
        instance = self.instance
        unit = attrs.get('unit', getattr(instance, 'unit', None))
        is_active = attrs.get('is_active', getattr(instance, 'is_active', True))

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
            'id', 'lease', 'tenant_name', 'amount', 'monthly_rent', 'months',
            'payment_date', 'method', 'reference', 'created_at',
        ]
        # monthly_rent and months are calculated by the system (step 6.2)
        read_only_fields = ['monthly_rent', 'months', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value