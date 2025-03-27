from __future__ import annotations

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient
from .models import LesCommunsConfig, LesCommunsProjet


class LesCommunsConnector(Connector):
    def on_project_event(self, project_id: int, event: WebhookEvent):
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
            "status": None,
            "programme": None,
            "collectivites": [],
            "competences": [],
            "leviers": [],
            "externalId": str(payload.get("id")),
        }

        data["status"] = {
            "DRAFT": "IDEE",
            "TO_PROCESS": "IDEE",
            "READY": "IDEE",
            "IN_PROGRESS": "EN_COURS",
            "DONE": "TERMINE",
            "STUCK": "ABANDONNE",
            "REJECTED": "ABANDONNE",
        }.get(payload.get("status"), "IDEE")

        if commune := payload.get("commune"):
            data["collectivites"].append({"type": "Commune", "code": commune["postal"]})

        if len(switchtenders := payload.get("switchtenders")):
            porteur = switchtenders[0]
            data["porteur"].update(
                {
                    "referentEmail": porteur.get("email"),
                    "referentPrenom": porteur.get("firstname"),
                    "referentNom": porteur.get("lastname"),
                }
            )

        return data

    def update_or_create_project_record(
        self, config: LesCommunsConfig, project_id: int, project_data: dict
    ):
        """
        Update a record related to a given project on LesCommuns side,
        or create it if it doesn't exist.
        """

        client = LesCommunsApiClient.from_config(config)

        project = LesCommunsProjet.objects.filter(recoco_id=project_id, config=config).first()

        if project:
            client.update_project(project_data)
            project.touch()
            project.save()
            return

        response = client.create_project(project_data)
        LesCommunsProjet.objects.create(
            recoco_id=project_id,
            lescommuns_id=response["id"],
            config=config,
        )
