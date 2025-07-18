from __future__ import annotations

from django.db import models


class WebhookEventStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSED = "PROCESSED", "Processed"
    INVALID = "INVALID", "Invalid"
    FAILED = "FAILED", "Failed"


class ObjectType(models.TextChoices):
    PROJECT = "projects.Project", "Project"
    SURVEY_ANSWER = "survey.Answer", "Answer"
    TAGGEDITEM = "taggit.TaggedItem", "TaggedItem"
    RECOMMENDATION = "tasks.Task", "Task"

    @property
    def is_project(self) -> bool:
        return self != self.RECOMMENDATION
