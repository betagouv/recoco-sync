from __future__ import annotations

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class Collectivite(BaseModel):
    type: str
    code: str

    class Config:
        alias_generator = to_camel


class Porteur(BaseModel):
    referent_email: str | None
    referent_prenom: str | None
    referent_nom: str | None
    code_siret: str | None = None
    referent_fonction: str | None = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class Projet(BaseModel):
    nom: str | None
    description: str | None
    porteur: Porteur | None = None
    budget_previsionnel: int | None = None
    date_debut_previsionnelle: str
    phase: str
    phase_statut: str
    programme: str | None = None
    collectivites: list[Collectivite] = []
    competences: list[str] = []
    leviers: list[str] = []
    external_id: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class Service(BaseModel):
    id: int
    name: str
    description: str | None = None
    sous_titre: str | None = None
    redirection_url: str | None = None
    logo_url: str | None = None
    extra_fields: list[dict[str, str]] = []
    is_listed: bool = True
    redirection_label: str | None = None
    iframe_url: str | None = None
    extend_label: str | None = None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
