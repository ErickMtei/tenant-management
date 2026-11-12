from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rentals.models import Lease, Unit


class Command(BaseCommand):
    help = 'Close leases that ended more than N days ago and free their units.'

    def add_arguments(self, parser):
        parser.add_argument('--grace-days', type=int, default=7)

    def handle(self, *args, **options):
        cutoff = timezone.localdate() - timedelta(days=options['grace_days'])
        leases = Lease.objects.filter(is_active=True, end_date__lt=cutoff)

        closed = 0
        for lease in leases:
            with transaction.atomic():
                lease.is_active = False
                lease.save(update_fields=['is_active'])
                Unit.objects.filter(pk=lease.unit_id).update(status=Unit.Status.VACANT)
                closed += 1

        self.stdout.write(self.style.SUCCESS(f'Closed {closed} lease(s).'))