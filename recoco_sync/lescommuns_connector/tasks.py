from __future__ import annotations

from celery import shared_task

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
