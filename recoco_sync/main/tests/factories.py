from __future__ import annotations

import uuid

import factory
import factory.fuzzy
from django.conf import settings

from recoco_sync.main.choices import ObjectType
from recoco_sync.main.models import WebhookConfig, WebhookEvent


class BaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    id = factory.LazyFunction(uuid.uuid4)


class WebhookConfigFactory(BaseFactory):
    class Meta:
        model = WebhookConfig

    api_url = settings.RECOCO_API_URL_EXAMPLE


class WebhookEventFactory(BaseFactory):
    class Meta:
        model = WebhookEvent

    webhook_uuid = factory.LazyFunction(uuid.uuid4)
    topic = "projects.Project/update"
    object_id = 1
    object_type = ObjectType.PROJECT

    remote_ip = factory.Faker("ipv4")
    headers = {}
    payload = {}

    webhook_config = factory.SubFactory(WebhookConfigFactory)
