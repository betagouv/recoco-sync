from __future__ import annotations

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient
from .models import ProjetLesCommuns


class LesCommunsConnector(Connector):
    les_communs_api_client: LesCommunsApiClient

    def __init__(self):
        super().__init__()
        self.les_communs_api_client = LesCommunsApiClient()

    def on_project_event(self, project_id: int, event: WebhookEvent):
        # ETQ collectivité, quand je dépose un projet sur un portail Reco-co,
        # je veux pouvoir le retrouver sur les autres sites qui font partie des "communs",
        # sans avoir besoin de resaisir les infos déjà données (enjeu du Dites le nous une fois).
        # On ne va pas envoyer les projets de tous les portails, on va commencer par UV

        if not event.webhook_config.site_domain.startswith("urbanbitaliz"):
            return

        _, project_data = next(self.fetch_projects_data(project_ids=[project_id]))

        proj = ProjetLesCommuns.objects.filter(projet_id=project_id).first()
        if proj is None:
            response = self.les_communs_api_client.create_project(project_data)
            ProjetLesCommuns.objects.create(
                projet_id=project_id, les_communs_project_id=response["id"]
            )
            return

        self.les_communs_api_client.update_project(project_data)

    def map_from_project_payload_object(self, payload, **kwargs):
        # Doc: https://les-communs-transition-ecologique-api-staging.osc-fr1.scalingo.io/api#/Projets/ProjetsController_create

        # TODO: find out status from recoco project
        # IDEE, FAISABILITE, EN_COURS, IMPACTE, ABANDONNE, TERMINE
        status = "IDEE"

        data = {
            "nom": payload.get("name"),
            "description": payload.get("description"),
            "porteur": {
                "codeSiret": None,
                "referentEmail": None,
                "referentTelephone": None,
                "referentPrenom": None,
                "referentNom": None,
                "referentFonction": None,
            },
            "budgetPrevisionnel": 0,
            "dateDebutPrevisionnelle": None,
            "status": status,
            "programme": None,
            "collectivites": [],
            "competences": [],
            "leviers": [],
            "externalId": str(payload.get("id")),
        }

        if commune := payload.get("commune"):
            data["collectivites"].append({"type": "Commune", "code": commune["postal"]})

        return data
