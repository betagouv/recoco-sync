from __future__ import annotations

from datetime import timedelta

from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone

from recoco_sync.main.models import WebhookEvent


class Command(BaseCommand):
    help = "Remove older payloads"

    def handle(self, *args, **options):
        events = WebhookEvent.objects.filter(
            Q(created__lt=timezone.now() - timedelta(days=30)) | Q(status__iexact="PROCESSED")
        )
        events.update(payload="")
