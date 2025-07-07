from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from django.conf import settings

from recoco_sync.main.choices import ObjectType
from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent

from .clients import LesCommunsApiClient
from .models import LesCommunsConfig, LesCommunsProjectSelection, LesCommunsProjet
from .schemas import Collectivite, Porteur, Projet
from .tasks import load_services_and_create_addons

logger = logging.getLogger(__name__)


class LesCommunsConnector(Connector):
    def on_webhook_event(self, object_id: int, object_type: ObjectType, event: WebhookEvent):
        project_id = self._extract_project_id_from_event(object_id, object_type, event)
        if project_id is None or not self._is_project_selection_enabled(project_id):
            return

        recommendation_id = object_id if object_type == ObjectType.RECOMMENDATION else None

        for config in LesCommunsConfig.objects.filter(
            enabled=True, webhook_config=event.webhook_config
        ):
            _, project_data = next(
                self.fetch_projects_data(project_ids=[project_id], config=config)
            )

            project = self.update_or_create_project_record(
                config=config, project_id=project_id, project_data=project_data
            )
            if recommendation_id:
                project.recommendation_id = recommendation_id
                project.save()

            load_services_and_create_addons.apply_async((project.id,), countdown=60)

    def _extract_project_id_from_event(
        self, object_id: int, object_type: ObjectType, event: WebhookEvent
    ) -> int | None:
        match object_type:
            case ObjectType.RECOMMENDATION:
                try:
                    if (
                        settings.LESCOMMUNS_RESOURCE_TAG_NAME
                        in event.object_data["resource"]["tags"]
                    ):
                        return event.object_data["project"]
                except KeyError as err:
                    logger.error(
                        f"Error processing webhook event for recommendation {object_id}: {err}"
                    )
                return None

            case ObjectType.PROJECT:
                return object_id

            case _:
                return None

    def _is_project_selection_enabled(self, project_id: int) -> bool:
        """
        Check if the project selection is enabled for the given project ID.
        Temporary trick to avoid creating lescommuns projects for all the recoco projects.
        """

        if not settings.LESCOMMUNS_PROJECT_SELECTION_ENABLED:
            return True
        return LesCommunsProjectSelection.objects.filter(
            recoco_id=project_id, config__enabled=True
        ).exists()

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
                code_siret=None,
                referent_fonction=None,
                referent_email=porteur_data.get("email"),
                referent_prenom=porteur_data.get("firstname"),
                referent_nom=porteur_data.get("lastname"),
            )

        data = Projet(
            nom=payload.get("name"),
            description=payload.get("description"),
            collectivites=collectivites,
            external_id=str(payload.get("id")),
            phase=self.phase_mapping(payload.get("status")),
            phase_statut=self.phase_statut_mapping(payload.get("status")),
            budget_previsionnel=None,
            date_debut_previsionnelle=datetime.fromisoformat(payload.get("created_on")).strftime(
                "%Y-%m-%d"
            ),
            porteur=porteur,
            programme=None,
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
    ) -> LesCommunsProjet:
        """
        Update a record related to a given project on LesCommuns side,
        or create it if it doesn't exist.
        """

        lescommuns_api_client = LesCommunsApiClient.from_config(config)

        # Update or create the project in LesCommuns
        if project := LesCommunsProjet.objects.filter(recoco_id=project_id, config=config).first():
            lescommuns_api_client.update_project(
                project_id=project.lescommuns_id, payload=project_data
            )
            project.touch()
            project.save()
            return project

        response = lescommuns_api_client.create_project(payload=project_data)
        return LesCommunsProjet.objects.create(
            recoco_id=project_id, lescommuns_id=response["id"], config=config
        )
