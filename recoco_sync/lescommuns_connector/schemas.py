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
