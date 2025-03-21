from __future__ import annotations

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient


class LesCommunsConnector(Connector):
    les_communs_api_client: LesCommunsApiClient

    def __init__(self):
        super().__init__()
        self.les_communs_api_client = LesCommunsApiClient()

    def update_project(self, project_id: int, event: WebhookEvent):
        # ETQ collectivité, quand je dépose un projet sur un portail Reco-co,
        # je veux pouvoir le retrouver sur les autres sites qui font partie des "communs",
        # sans avoir besoin de resaisir les infos déjà données (enjeu du Dites le nous une fois).
        # On ne va pas envoyer les projets de tous les portails, on va commencer par UV

        if not event.webhook_config.site_domain.startswith("urbanbitaliz"):
            return

        _, project_data = next(self.fetch_projects_data(project_ids=[project_id]))

        match event.topic:
            case "projects.Project/create":
                self.les_communs_api_client.create_project(project_data)
            case "projects.Project/update":
                self.les_communs_api_client.update_project(project_data)
            case "projects.Project/delete":
                self.les_communs_api_client.delete_project(project_data)
            case _:
                pass
