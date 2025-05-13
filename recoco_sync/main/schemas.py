from __future__ import annotations

from typing import Any

from ninja import Schema
from pydantic import AliasPath, BaseModel, Field, computed_field, field_validator


class WebhookEventSchema(Schema):
    topic: str
    object: dict[str, Any]
    object_type: str
    webhook_uuid: str


class Project(BaseModel):
    name: str
    description: str | None
    created_on: str = Field(alias="created")
    updated_on: str = Field(alias="modified")
    location: str | None
    latitude: float | None
    longitude: float | None
    org_name: str | None = Field(alias="organization")
    inactive_since: str | None
    status: str
    commune_name: str | None = Field(
        validation_alias=AliasPath("commune", "name"),
        alias="city",
    )
    commune_insee: str | None = Field(
        validation_alias=AliasPath("commune", "insee"),
        alias="insee",
    )
    commune_postal: str | None = Field(
        validation_alias=AliasPath("commune", "postal"),
        alias="postal_code",
    )
    commune_department: str | None = Field(
        validation_alias=AliasPath("commune", "department", "name"),
        alias="department",
    )
    commune_department_code: str | None = Field(
        validation_alias=AliasPath("commune", "department", "code"),
        alias="department_code",
    )
    commune_region: str | None = Field(
        validation_alias=AliasPath("commune", "department", "region", "name"),
        alias="region",
    )
    commune_region_code: str | None = Field(
        validation_alias=AliasPath("commune", "department", "region", "code"),
        alias="region_code",
    )
    tags: list[str] = Field(default_factory=list)
    advisors_note: str | None

    class Config:
        populate_by_name = True

    @field_validator("tags", mode="after")
    @classmethod
    def compute_tags(cls, value: Any) -> str:
        return ",".join(value)

    @computed_field
    @property
    def active(self) -> bool:
        return self.inactive_since is None
