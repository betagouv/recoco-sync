from __future__ import annotations

from datetime import datetime
from typing import Any

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient
from .models import LesCommunsConfig, LesCommunsProjet
from .schemas import Collectivite, Porteur, Projet


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

    def map_from_project_payload_object(self, payload: dict[str, Any], **kwargs) -> dict[str, Any]:
        # Doc: https://les-communs-transition-ecologique-api-staging.osc-fr1.scalingo.io/api#/Projets/ProjetsController_create

        collectivites = []
        if commune := payload.get("commune"):
            collectivites.append(Collectivite(type="Commune", code=commune["insee"]))

        porteur = None
        if len(switchtenders := payload.get("switchtenders")):
            porteur_data = switchtenders[0]
            porteur = Porteur(
                referentEmail=porteur_data.get("email"),
                referentPrenom=porteur_data.get("firstname"),
                referentNom=porteur_data.get("lastname"),
            )

        data = Projet(
            nom=payload.get("name"),
            description=payload.get("description"),
            collectivites=collectivites,
            externalId=str(payload.get("id")),
            phase=self.phase_mapping(payload.get("status")),
            phaseStatut=self.phase_statut_mapping(payload.get("status")),
            dateDebutPrevisionnelle=datetime.fromisoformat(payload.get("created_on")).strftime(
                "%Y-%m-%d"
            ),
            porteur=porteur,
        )

        return data.model_dump(by_alias=True)

    @staticmethod
    def phase_mapping(status: str) -> str:
        return {
            "DRAFT": "Idée",
            "TO_PROCESS": "Idée",
            "READY": "Idée",
            "IN_PROGRESS": "Idée",
            "DONE": "Idée",
            "STUCK": "Idée",
            "REJECTED": "Idée",
        }.get(status, "Idée")

    @staticmethod
    def phase_statut_mapping(status: str) -> str:
        return {
            "DRAFT": "En cours",
            "TO_PROCESS": "En cours",
            "READY": "En cours",
            "IN_PROGRESS": "En cours",
            "DONE": "Terminé",
            "STUCK": "Bloqué",
            "REJECTED": "Abandonné",
        }.get(status, "En cours")

    def map_from_survey_answer_payload_object(
        self, payload: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        return {}

    def update_or_create_project_record(
        self, config: LesCommunsConfig, project_id: int, project_data: dict
    ):
        """
        Update a record related to a given project on LesCommuns side,
        or create it if it doesn't exist.
        """

        project = LesCommunsProjet.objects.filter(recoco_id=project_id, config=config).first()

        if project:
            LesCommunsApiClient().update_project(
                project_id=project.lescommuns_id, payload=project_data
            )
            project.touch()
            project.save()
            return

        response = LesCommunsApiClient().create_project(payload=project_data)
        LesCommunsProjet.objects.create(
            recoco_id=project_id,
            lescommuns_id=response["id"],
            config=config,
        )
