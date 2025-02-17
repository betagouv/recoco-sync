from __future__ import annotations

import pytest

from .factories import WebhookConfigFactory


@pytest.mark.django_db
def test_webhook_config_code():
    config1 = WebhookConfigFactory()
    config2 = WebhookConfigFactory()
    assert config1.code != config2.code
    assert len(config1.code) == 12

    config3 = WebhookConfigFactory(code="test")
    assert config3.code == "test"
