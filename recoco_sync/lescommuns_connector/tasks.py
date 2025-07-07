from __future__ import annotations

from celery import shared_task

from recoco_sync.main.clients import RecocoApiClient

from .clients import LesCommunsApiClient
from .models import LesCommunsProjet


@shared_task
def load_lescommuns_services(project_id: int):
    try:
        project = LesCommunsProjet.objects.select_related("config").get(id=project_id)
    except LesCommunsProjet.DoesNotExist as err:
        raise ValueError(f"LesCommunsProjet with id={project_id} does not exist") from err

    if not project.config.enabled:
        raise ValueError(f"LesCommunsConfig with id={project.config_id} is not enabled")

    services = LesCommunsApiClient.from_config(project.config).get_project_services(
        project_id=project.lescommuns_id
    )
    if len(services):
        project.services = services
        project.save()


@shared_task
def update_or_create_resource_addons(project_id: int):
    try:
        project = LesCommunsProjet.objects.select_related("config__webhook_config").get(
            id=project_id
        )
    except LesCommunsProjet.DoesNotExist as err:
        raise ValueError(f"LesCommunsProjet with id={project_id} does not exist") from err

    if not project.config.enabled:
        raise ValueError(f"LesCommunsConfig with id={project.config_id} is not enabled")

    webhook_config = project.config.webhook_config
    if not webhook_config.enabled:
        raise ValueError(f"WebhookConfig with id={webhook_config.id} is not enabled")

    if not project.is_service_ready:
        return

    recoco_api_client = RecocoApiClient(api_url=webhook_config.api_url)

    # fetch existing addons
    existing_addons = recoco_api_client.get_resource_addons(
        recommendation_id=project.recommendation_id
    )

    # update or create addons based on project.services
    if existing_addons.get("count") == 0:
        recoco_api_client.create_resource_addon(
            payload={
                "recommendation": project.recommendation_id,
                "nature": "lescommuns",
                "data": project.services,
                "enabled": True,
            }
        )
    else:
        recoco_api_client.update_resource_addon(
            addon_id=existing_addons["results"][0]["id"],
            payload={
                "recommendation": project.recommendation_id,
                "nature": "lescommuns",
                "data": project.services,
                "enabled": True,
            },
        )
