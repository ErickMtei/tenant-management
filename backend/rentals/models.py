import calendar
from datetime import date
from django.db import models
from django.conf import settings


def add_months(start, months):
    """Add months to a date. If the day does not exist in the target month,
    use the last day of that month (e.g. Oct 31 + 1 month = Nov 30)."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

class Property(models.Model):
    """A building or compound that contains rentable units."""

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'properties'

    def __str__(self):
        return self.name


class Unit(models.Model):
    """A single rentable room or apartment inside a property."""

    class Status(models.TextChoices):
        VACANT = 'vacant', 'Vacant'
        OCCUPIED = 'occupied', 'Occupied'
        MAINTENANCE = 'maintenance', 'Under maintenance'

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='units'
    )
    unit_number = models.CharField(max_length=20)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.VACANT
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['property', 'unit_number'], name='unique_unit_per_property'
            )
        ]

    def __str__(self):
        return f'{self.property.name} - {self.unit_number}'


class Tenant(models.Model):
    """A person who rents a unit."""

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    national_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tenant_profile',
    )

    def __str__(self):
        return self.full_name


class Lease(models.Model):
    """A rental agreement. end_date is calculated from payments, never typed."""

    tenant = models.ForeignKey(
        Tenant, on_delete=models.PROTECT, related_name='leases'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField(editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tenant.full_name} -> {self.unit}'


class Payment(models.Model):
    """A prepaid rent payment. It locks in the rent used and the months bought."""

    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        MOBILE_MONEY = 'mobile_money', 'Mobile money'
        BANK = 'bank', 'Bank transfer'

    lease = models.ForeignKey(
        Lease, on_delete=models.PROTECT, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    months = models.PositiveIntegerField()
    payment_date = models.DateField()
    method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH
    )
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.lease} - {self.amount} ({self.months} months)'