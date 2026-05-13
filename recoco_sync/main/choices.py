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
    USER = "home.UserProfile", "UserProfile"

    @property
    def is_project(self) -> bool:
        # this represents not the object from webhook directly but how we use it in this code
        # recommendation is only used for les_communs and grist only reads projects data
        return self != self.RECOMMENDATION
