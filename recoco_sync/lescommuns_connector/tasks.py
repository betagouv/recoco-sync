from __future__ import annotations

from celery import shared_task

from .clients import LesCommunsApiClient
from .models import LesCommunsConfig, LesCommunsProjet


@shared_task
def load_lescommuns_services(config_id: str, project_id: int):
    try:
        config = LesCommunsConfig.objects.get(id=config_id)
    except LesCommunsConfig.DoesNotExist as err:
        raise ValueError(f"LesCommunsConfig with id={config_id} does not exist") from err

    if not config.enabled:
        raise ValueError(f"LesCommunsConfig with id={config_id} is not enabled")

    try:
        project = LesCommunsProjet.objects.get(id=project_id)
    except LesCommunsProjet.DoesNotExist as err:
        raise ValueError(
            f"LesCommunsProjet with id={project_id} and config_id={config_id} does not exist"
        ) from err

    services = LesCommunsApiClient.from_config(config).get_project_services(
        project_id=project.lescommuns_id
    )
    if len(services):
        project.services = services
        project.save()
