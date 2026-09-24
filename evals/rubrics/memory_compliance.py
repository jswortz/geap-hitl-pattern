"""Rubric 3: Brand Memory & Claim Compliance (PRD Section 13.3)."""

import json
from typing import Any, Dict, List


def evaluate_memory_compliance(
    brief_dict: Dict[str, Any],
    expected_directives: List[str],
    prohibited_terms: List[str],
) -> Dict[str, Any]:
    """Confirm 0% presence of prohibited terms and >= 90% coverage of expected directives."""
    serialized = json.dumps(brief_dict).lower()

    violated_terms = [t for t in prohibited_terms if t.lower() in serialized]
    if not expected_directives:
        directive_coverage = 1.0
        matched_directives = []
    else:
        matched_directives = [
            d for d in expected_directives if d.lower() in serialized
        ]
        directive_coverage = len(matched_directives) / len(expected_directives)

    passed = (len(violated_terms) == 0) and (directive_coverage >= 0.90)
    return {
        "passed": passed,
        "score": directive_coverage if len(violated_terms) == 0 else 0.0,
        "directive_coverage": directive_coverage,
        "matched_directives": matched_directives,
        "prohibited_violations": violated_terms,
    }
