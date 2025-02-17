from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

from .clients import GristApiClient, RecocoApiClient
from .constants import default_columns_spec
from .models import GristColumn, GristColumnFilter, GristConfig, GritColumnConfig

logger = logging.getLogger(__name__)


def update_or_create_project_record(config: GristConfig, project_id: int, project_data: dict):
    """
    Update a record related to a givent project, in a Grist table,
    or create it if it doesn't exist.
    """

    client = GristApiClient.from_config(config)

    resp = client.get_records(
        table_id=config.table_id,
        filter={"object_id": [project_id]},
    )

    if len(records := resp["records"]):
        client.update_records(
            table_id=config.table_id,
            records={
                records[0]["id"]: project_data,
            },
        )
        return

    client.create_records(
        table_id=config.table_id,
        records=[{"object_id": project_id} | project_data],
    )


def fetch_projects_data(
    config: GristConfig, project_ids: list[int] | None = None
) -> Generator[tuple[int, dict]]:
    """Fetch data related to projects from Recoco API."""

    recoco_client = RecocoApiClient(timeout=60)

    if project_ids:
        projects = [recoco_client.get_project(project_id=project_id) for project_id in project_ids]
    else:
        projects = recoco_client.get_projects()

    for project in projects:
        project_data = map_from_project_payload_object(obj=project, config=config)

        sessions = recoco_client.get_survey_sessions(project_id=project["id"])
        if sessions["count"] > 0:
            answers = recoco_client.get_survey_session_answers(
                session_id=sessions["results"][0]["id"]
            )
            for answer in answers["results"]:
                project_data.update(
                    map_from_survey_answer_payload_object(obj=answer, config=config)
                )

        yield project["id"], project_data


def grist_table_exists(config: GristConfig) -> bool:
    """Check if a table exists in Grist."""

    return GristApiClient.from_config(config).table_exists(table_id=config.table_id)


def check_table_columns_consistency(config: GristConfig) -> bool:
    """Check the columns of a table in Grist are consistent with the config."""

    config_table_columns = config.table_columns
    config_table_columns_keys = [t["id"] for t in config_table_columns]

    remote_table_columns = GristApiClient.from_config(config).get_table_columns(
        table_id=config.table_id
    )
    remote_table_columns = [
        {"id": t["id"], "fields": {k: t["fields"][k] for k in ("label", "type")}}
        for t in remote_table_columns
        if t["id"] in config_table_columns_keys
    ]

    return sorted(remote_table_columns, key=lambda x: x["id"]) == sorted(
        config_table_columns, key=lambda x: x["id"]
    )


def check_column_filters(filters: list[GristColumnFilter], obj: dict[str, Any]) -> bool:
    for filter in filters:
        if not filter.check_object(obj):
            return False
    return True


def map_from_project_payload_object(obj: dict[str, Any], config: GristConfig) -> dict[str, Any]:
    """Map a project payload object respecting a Grist configuration."""

    if not len(available_keys := config.table_headers):
        return {}

    try:
        data = {
            "name": obj["name"],
            "context": obj["description"],
            "city": obj["commune"]["name"],
            "postal_code": int(obj["commune"]["postal"]),
            "insee": int(obj["commune"]["insee"]),
            "department": obj["commune"]["department"]["name"],
            "department_code": int(obj["commune"]["department"]["code"]),
            "location": obj["location"],
            "tags": ",".join(obj["tags"]),
        }
    except (KeyError, ValueError) as exc:
        logger.error(f"Error while mapping project #{obj["id"]} payload object: {exc}")
        return {}

    return {k: data[k] for k in available_keys if k in data}


def map_from_survey_answer_payload_object(  # noqa: C901
    obj: dict[str, Any], config: GristConfig
) -> dict[str, Any]:
    """Map a survey answer payload object respecting a Grist configuration."""

    def _format_choices(_obj):
        return ",".join([c["text"] for c in _obj["choices"]])

    if not len(available_keys := config.table_headers):
        return {}

    data = {}

    map_question_slugs_columns = {
        "autres-programmes-et-contrats": "dependencies",
        "boussole": "ecological_transition_compass",
        "budget-previsionnel": "budget",
        "calendrier": "calendar",
        "description-de-laction": "action",
        "diagnostic-anct": "diagnostic_anct",
        "indicateurs-de-suivi-et-deval": "evaluation_indicator",
        "maitre-douvrage-2": "ownership",
        "maturite-du-projet": "maturity",
        "partage-a-la-commune": "diagnostic_is_shared",
        "partenaires-2": "partners",
        "perimetre": "perimeter",
        "plan-de-financement-definitif": "final_financing_plan",
        "plan-de-financement-previsionnel": "forecast_financing_plan",
        "procedures-administratives": "administrative_procedures",
        "thematiques-2": "topics",
    }

    match question_slug := obj["question"]["slug"]:
        case "thematiques-2" | "autres-programmes-et-contrats" | "perimetre" | "maturite-du-projet":
            data.update(
                {
                    map_question_slugs_columns[question_slug]: _format_choices(obj),
                    f"{map_question_slugs_columns[question_slug]}_comment": obj["comment"],
                }
            )

        case "budget-previsionnel":
            try:
                data.update({map_question_slugs_columns[question_slug]: float(obj["comment"])})
            except ValueError:
                pass

        case (
            "diagnostic-anct"
            | "calendrier"
            | "plan-de-financement-definitif"
            | "plan-de-financement-previsionnel"
        ):
            data.update(
                {
                    map_question_slugs_columns[question_slug]: obj["comment"],
                    f"{map_question_slugs_columns[question_slug]}_attachment": obj["attachment"],
                }
            )

        case "partage-a-la-commune":
            data.update(
                {
                    map_question_slugs_columns[question_slug]: obj["values"][0] == "Oui",
                }
            )

        case (
            "boussole"
            | "description-de-laction"
            | "indicateurs-de-suivi-et-deval"
            | "maturite-du-projet"
            | "partenaires-2"
            | "procedures-administratives"
            | "plan-de-financement-definitif"
            | "maitre-douvrage-2"
        ):
            data.update({map_question_slugs_columns[question_slug]: obj["comment"]})

        case _:
            logger.info(f"Unhandled question: {obj['question']['text_short']}")

    return {k: data[k] for k in available_keys if k in data}


def update_or_create_columns():
    for col_id, col_data in default_columns_spec.items():
        GristColumn.objects.update_or_create(
            col_id=col_id,
            defaults=col_data,
        )


def update_or_create_columns_config(config: GristConfig):
    position = 0
    for col_id in default_columns_spec.keys():
        GritColumnConfig.objects.update_or_create(
            grist_column=GristColumn.objects.get(col_id=col_id),
            grist_config=config,
            defaults={"position": position},
        )
        position += 10
