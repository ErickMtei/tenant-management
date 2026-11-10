from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lease, Payment, Unit


def parse_days(value, default=30):
    """Read ?days=NN from the query string and validate it."""
    if not value:
        return default
    try:
        days = int(value)
    except ValueError:
        raise ValidationError({'days': 'Must be a whole number.'})
    if days < 1 or days > 365:
        raise ValidationError({'days': 'Must be between 1 and 365.'})
    return days


class ExpiringLeasesReportView(APIView):
    """GET /api/reports/expiring/?days=30 - active leases ending soon.

    Includes leases that already ended but are still marked active,
    because those tenants need to be followed up too.
    """

    def get(self, request):
        days = parse_days(request.query_params.get('days'))
        today = timezone.localdate()
        limit = today + timedelta(days=days)

        leases = (
            Lease.objects.filter(is_active=True, end_date__lte=limit)
            .select_related('tenant', 'unit__property')
            .order_by('end_date')
        )

        results = [
            {
                'lease_id': lease.id,
                'tenant_id': lease.tenant_id,
                'tenant_name': lease.tenant.full_name,
                'phone_number': lease.tenant.phone_number,
                'unit': str(lease.unit),
                'start_date': lease.start_date,
                'end_date': lease.end_date,
                'days_left': (lease.end_date - today).days,
            }
            for lease in leases
        ]
        return Response(
            {'days': days, 'count': len(results), 'results': results}
        )


class SummaryReportView(APIView):
    """GET /api/reports/summary/?month=2026-10 - occupancy and money received."""

    def get(self, request):
        today = timezone.localdate()
        month = request.query_params.get('month')

        if month:
            try:
                year, mon = (int(part) for part in month.split('-'))
                start = today.replace(year=year, month=mon, day=1)
            except (ValueError, TypeError):
                raise ValidationError(
                    {'month': 'Use the format YYYY-MM, e.g. 2026-10.'}
                )
        else:
            start = today.replace(day=1)

        # First day of the next month
        if start.month == 12:
            next_start = start.replace(year=start.year + 1, month=1)
        else:
            next_start = start.replace(month=start.month + 1)

        received = Payment.objects.filter(
            payment_date__gte=start, payment_date__lt=next_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        units_by_status = {
            row['status']: row['total']
            for row in Unit.objects.values('status').annotate(total=Count('id'))
        }

        expiring_soon = Lease.objects.filter(
            is_active=True, end_date__lte=today + timedelta(days=30)
        ).count()

        return Response(
            {
                'month': start.strftime('%Y-%m'),
                'units': {
                    'total': sum(units_by_status.values()),
                    'vacant': units_by_status.get('vacant', 0),
                    'occupied': units_by_status.get('occupied', 0),
                    'maintenance': units_by_status.get('maintenance', 0),
                },
                'received': received,
                'active_leases': Lease.objects.filter(is_active=True).count(),
                'expiring_soon': expiring_soon,
            }
        )