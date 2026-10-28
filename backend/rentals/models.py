from django.db import models


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

    def __str__(self):
        return self.full_name


class Lease(models.Model):
    """A rental agreement between a tenant and a unit."""

    tenant = models.ForeignKey(
        Tenant, on_delete=models.PROTECT, related_name='leases'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tenant.full_name} -> {self.unit}'


class Payment(models.Model):
    """A rent payment made against a lease."""

    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        MOBILE_MONEY = 'mobile_money', 'Mobile money'
        BANK = 'bank', 'Bank transfer'

    lease = models.ForeignKey(
        Lease, on_delete=models.PROTECT, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    period_month = models.DateField(
        help_text='First day of the month this payment covers, e.g. 2026-11-01'
    )
    method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH
    )
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.lease} - {self.amount} ({self.period_month:%Y-%m})'