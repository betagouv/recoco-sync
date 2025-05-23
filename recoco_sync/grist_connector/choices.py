from __future__ import annotations

from django.db import models


class GristColumnType(models.TextChoices):
    BOOL = "boolean", "Bool"
    CHOICE = "choice", "Choice"
    CHOICE_LIST = "choice_list", "ChoiceList"
    DATE = "date", "Date"
    DATETIME = "datetime", "DateTime:Europe/Amsterdam"
    INTEGER = "integer", "Int"
    NUMERIC = "numeric", "Numeric"
    TEXT = "text", "Text"


class FilterOperator(models.TextChoices):
    EQUAL = "eq", "Equal"
    I_EQUAL = "ieq", "Equal (case-insensitive)"
    NOT_EQUAL = "ne", "Not equal"
    I_NOT_EQUAL = "ine", "Not equal (case-insensitive)"
    CONTAINS = "contains", "Contains"
    I_CONTAINS = "icontains", "Contains (case-insensitive)"
