from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user. Every person who logs in has exactly one role."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        ACCOUNTANT = 'accountant', 'Accountant'
        TENANT = 'tenant', 'Tenant'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TENANT)
    phone_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Superusers created with createsuperuser are always admins
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)