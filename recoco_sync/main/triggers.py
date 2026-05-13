from __future__ import annotations

from .choices import WebhookEventStatus
from .models import WebhookEvent
from .tasks import process_webhook_event


def on_webhook_event_commit(event: WebhookEvent) -> None:
    if event.status != WebhookEventStatus.PENDING:
        return
    # todo do not commit removing delay
    process_webhook_event(event.id)
