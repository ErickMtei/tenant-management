import calendar
from datetime import datetime
from decimal import Decimal
from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lease, Unit


def parse_month(value):
    """Turn '2026-10' into date(2026, 10, 1). Defaults to the current month."""
    if not value:
        return timezone.localdate().replace(day=1)
    try:
        return datetime.strptime(value, '%Y-%m').date()
    except ValueError:
        raise ValidationError({'month': 'Use the format YYYY-MM, e.g. 2026-10.'})


def lease_balances(month_start):
    """Active leases that cover the given month, with paid amount and balance."""
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    month_end = month_start.replace(day=last_day)

    return (
        Lease.objects.filter(is_active=True, start_date__lte=month_end)
        .filter(Q(end_date__isnull=True) | Q(end_date__gte=month_start))
        .select_related('tenant', 'unit__property')
        .annotate(
            paid=Coalesce(
                Sum('payments__amount', filter=Q(payments__period_month=month_start)),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .annotate(balance=F('unit__monthly_rent') - F('paid'))
    )


class ArrearsReportView(APIView):
    """GET /api/reports/arrears/?month=2026-10 - tenants who owe rent."""

    def get(self, request):
        month_start = parse_month(request.query_params.get('month'))
        leases = lease_balances(month_start).filter(balance__gt=0).order_by('-balance')

        results = [
            {
                'lease_id': lease.id,
                'tenant_id': lease.tenant_id,
                'tenant_name': lease.tenant.full_name,
                'phone_number': lease.tenant.phone_number,
                'unit': str(lease.unit),
                'monthly_rent': lease.unit.monthly_rent,
                'paid': lease.paid,
                'balance': lease.balance,
            }
            for lease in leases
        ]
        return Response(
            {
                'month': month_start.strftime('%Y-%m'),
                'count': len(results),
                'total_outstanding': sum((r['balance'] for r in results), Decimal('0')),
                'results': results,
            }
        )


class SummaryReportView(APIView):
    """GET /api/reports/summary/?month=2026-10 - occupancy and rent collection."""

    def get(self, request):
        month_start = parse_month(request.query_params.get('month'))
        leases = list(lease_balances(month_start))

        expected = sum((l.unit.monthly_rent for l in leases), Decimal('0'))
        collected = sum((l.paid for l in leases), Decimal('0'))
        units_by_status = {
            row['status']: row['total']
            for row in Unit.objects.values('status').annotate(total=Count('id'))
        }

        return Response(
            {
                'month': month_start.strftime('%Y-%m'),
                'units': {
                    'total': sum(units_by_status.values()),
                    'vacant': units_by_status.get('vacant', 0),
                    'occupied': units_by_status.get('occupied', 0),
                    'maintenance': units_by_status.get('maintenance', 0),
                },
                'rent': {
                    'expected': expected,
                    'collected': collected,
                    'outstanding': expected - collected,
                },
            }
        )