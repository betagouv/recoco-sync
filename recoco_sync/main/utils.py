from __future__ import annotations

from enum import Enum
from typing import Any


class QuestionType(Enum):
    REGULAR = "regular"
    YES_NO = "yes_no"
    YES_NO_MAYBE = "yes_no_maybe"
    MULTIPLE = "multiple"


def get_question_type(question: dict[str, Any]) -> QuestionType:
    is_mutliple = question.get("is_multiple", False)
    if is_mutliple:
        return QuestionType.MULTIPLE

    choices_values = [choice.get("text") for choice in question.get("choices", [])]
    joined_choices = "/".join(sorted(choices_values)).lower().replace(" ", "")
    if joined_choices == "non/oui":
        return QuestionType.YES_NO
    if joined_choices == "jenesaispas/non/oui":
        return QuestionType.YES_NO_MAYBE

    return QuestionType.REGULAR
