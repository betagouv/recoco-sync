from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from recoco_sync.main.choices import ObjectType, WebhookEventStatus
from recoco_sync.main.tasks import process_webhook_event

from .factories import WebhookEventFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_id, object_type, object_payload, expected_object_id, expected_object_type",
    [
        (999, ObjectType.PROJECT, {"project": 999}, 999, ObjectType.PROJECT),
        (888, ObjectType.SURVEY_ANSWER, {"project": 999}, 999, ObjectType.PROJECT),
        # (ObjectType.RECOMMENDATION, 666, {}),
    ],
)
def test_task_triggered_and_event_saved(
    object_id, object_type, object_payload, expected_object_id, expected_object_type
):
    event = WebhookEventFactory(
        object_id=object_id,
        object_type=object_type,
        payload={"object": object_payload},
    )

    fake_connector = MagicMock()

    with patch("recoco_sync.main.tasks.get_connectors", Mock(return_value=[fake_connector])):
        process_webhook_event(event_id=event.id)

    fake_connector.on_webhook_event.assert_called_once_with(
        object_id=expected_object_id, object_type=expected_object_type, event=event
    )

    event.refresh_from_db()
    assert event.status == WebhookEventStatus.PROCESSED


@pytest.mark.django_db
def test_event_does_not_exist():
    with patch("recoco_sync.main.tasks.logger.error") as logger_mock:
        process_webhook_event(event_id=1)
    logger_mock.assert_called_once_with("WebhookEvent with id=1 does not exist")
