"""Rubric 1: Strict Schema Conformance (PRD Section 13.3)."""

from typing import Any, Dict
from pydantic import ValidationError
from services.trend_agent.schemas import InitiativeIdeaBrief


def evaluate_schema_conformance(brief_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that agent response deserializes cleanly into InitiativeIdeaBrief."""
    try:
        validated = InitiativeIdeaBrief.model_validate(brief_dict)
        return {
            "passed": True,
            "score": 1.0,
            "initiative_id": validated.initiative_id,
            "errors": [],
        }
    except ValidationError as err:
        return {
            "passed": False,
            "score": 0.0,
            "errors": [str(e) for e in err.errors()],
        }
