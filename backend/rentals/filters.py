import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    # /api/payments/?date_from=2026-10-01&date_to=2026-10-31
    date_from = django_filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='payment_date', lookup_expr='lte')

    class Meta:
        model = Payment
        fields = ['lease', 'lease__tenant', 'method', 'period_month']