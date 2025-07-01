from __future__ import annotations

import factory

from recoco_sync.lescommuns_connector.models import (
    LesCommunsConfig,
    LesCommunsProjectSelection,
    LesCommunsProjet,
)
from recoco_sync.main.tests.factories import BaseFactory, WebhookConfigFactory


class LesCommunsConfigFactory(BaseFactory):
    class Meta:
        model = LesCommunsConfig

    name = factory.Faker("word")
    webhook_config = factory.SubFactory(WebhookConfigFactory)
    api_key = factory.Faker("sha256")
    enabled = True


class LesCommunsProjectSelectionFactory(BaseFactory):
    class Meta:
        model = LesCommunsProjectSelection

    recoco_id = factory.Sequence(lambda n: n + 1)
    config = factory.SubFactory(LesCommunsConfigFactory)


class LesCommunsProjetFactory(BaseFactory):
    class Meta:
        model = LesCommunsProjet

    lescommuns_id = factory.Sequence(lambda n: n + 1)
    recoco_id = factory.Sequence(lambda n: n + 1)
    config = factory.SubFactory(LesCommunsConfigFactory)
