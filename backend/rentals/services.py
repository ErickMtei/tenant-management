from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from .models import Lease, Payment, Unit, add_months


def months_for_amount(amount, monthly_rent):
    """Return how many whole months an amount buys. Reject partial payments."""
    if monthly_rent <= 0:
        raise ValidationError({'amount': 'The unit has no valid monthly rent.'})
    months, remainder = divmod(amount, monthly_rent)
    if months < 1 or remainder != 0:
        raise ValidationError(
            {'amount': f'Amount must be a whole multiple of the monthly rent ({monthly_rent}).'}
        )
    return int(months)


@transaction.atomic
def create_lease_with_payment(
    *, tenant, unit, start_date, amount, payment_date, method='cash', reference=''
):
    """Create a lease and its first payment together. Nothing is saved if any step fails."""
    # Lock the unit row so two people cannot rent it at the same moment
    unit = Unit.objects.select_for_update().get(pk=unit.pk)

    if unit.status != Unit.Status.VACANT:
        raise ValidationError({'unit': 'This unit is not vacant.'})
    if Lease.objects.filter(unit=unit, is_active=True).exists():
        raise ValidationError({'unit': 'This unit already has an active lease.'})

    months = months_for_amount(amount, unit.monthly_rent)

    lease = Lease.objects.create(
        tenant=tenant,
        unit=unit,
        start_date=start_date,
        end_date=add_months(start_date, months),
        is_active=True,
    )
    Payment.objects.create(
        lease=lease,
        amount=amount,
        monthly_rent=unit.monthly_rent,
        months=months,
        payment_date=payment_date,
        method=method,
        reference=reference,
    )
    unit.status = Unit.Status.OCCUPIED
    unit.save(update_fields=['status'])
    return lease


@transaction.atomic
def add_payment(*, lease, amount, payment_date, method='cash', reference=''):
    """Record a payment that extends an existing lease."""
    lease = Lease.objects.select_for_update().select_related('unit').get(pk=lease.pk)

    if not lease.is_active:
        raise ValidationError({'lease': 'This lease is no longer active.'})

    # Rent is the unit's current price. Old payments keep their own locked price.
    monthly_rent = lease.unit.monthly_rent
    months = months_for_amount(amount, monthly_rent)

    payment = Payment.objects.create(
        lease=lease,
        amount=amount,
        monthly_rent=monthly_rent,
        months=months,
        payment_date=payment_date,
        method=method,
        reference=reference,
    )

    # Always count from start_date using ALL months paid. This avoids date drift
    # (e.g. Oct 31 -> Nov 30 -> Dec 30 instead of Dec 31).
    total_months = lease.payments.aggregate(total=Sum('months'))['total']
    lease.end_date = add_months(lease.start_date, total_months)
    lease.save(update_fields=['end_date'])
    return payment