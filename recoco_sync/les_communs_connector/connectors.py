from __future__ import annotations

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient
from .models import LesCommunsConfig, LesCommunsProjet


class LesCommunsConnector(Connector):
    def on_project_event(self, project_id: int, event: WebhookEvent):
        # ETQ collectivité, quand je dépose un projet sur un portail Reco-co,
        # je veux pouvoir le retrouver sur les autres sites qui font partie des "communs",
        # sans avoir besoin de resaisir les infos déjà données (enjeu du Dites le nous une fois).
        # On ne va pas envoyer les projets de tous les portails, on va commencer par UV

        for config in LesCommunsConfig.objects.filter(
            enabled=True, webhook_config=event.webhook_config
        ):
            for _, project_data in self.fetch_projects_data(
                project_ids=[project_id], config=config
            ):
                self.update_or_create_project_record(
                    config=config, project_id=project_id, project_data=project_data
                )

    def get_recoco_api_client(self, **kwargs):
        config: LesCommunsConfig = kwargs.get("config")
        return super().get_recoco_api_client(api_url=config.webhook_config.api_url)

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

    def update_or_create_project_record(
        self, config: LesCommunsConfig, project_id: int, project_data: dict
    ):
        """
        Update a record related to a given project on LesCommuns side,
        or create it if it doesn't exist.
        """

        client = LesCommunsApiClient.from_config(config)

        proj = LesCommunsProjet.objects.filter(projet_id=project_id, config=config).first()

        if proj:
            client.update_project(project_data)
            proj.touch()
            proj.save()
            return

        response = client.create_project(project_data)
        LesCommunsProjet.objects.create(
            projet_id=project_id,
            les_communs_project_id=response["id"],
            config=config,
        )
