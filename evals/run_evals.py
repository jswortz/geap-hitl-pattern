"""Automated Evaluation Harness Runner for Antigravity (PRD Section 13.4)."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from evals.rubrics.grounding_accuracy import evaluate_grounding_accuracy
from evals.rubrics.memory_compliance import evaluate_memory_compliance
from evals.rubrics.schema_conformance import evaluate_schema_conformance
from evals.rubrics.tone_alignment import evaluate_tone_alignment
from services.trend_agent.agent import trend_agent


async def run_evaluation_suite(
    dataset_path: str = "evals/test_dataset.jsonl",
    output_path: str = "evals/results/latest_run.json",
) -> Dict[str, Any]:
    dataset_file = Path(dataset_path)
    cases = [
        json.loads(line)
        for line in dataset_file.read_text().splitlines()
        if line.strip()
    ]

    results: List[Dict[str, Any]] = []
    all_passed = True

    for case in cases:
        agent_out = await trend_agent.generate_brief(
            brand_id=case["brand_id"],
            category=case["category"],
            search_query=case["search_query"],
        )
        brief = agent_out["brief"]
        verified_urls = agent_out["verified_search_urls"]

        r1 = evaluate_schema_conformance(brief)
        r2 = evaluate_grounding_accuracy(brief, verified_urls)
        r3 = evaluate_memory_compliance(
            brief,
            expected_directives=case.get("expected_directives", []),
            prohibited_terms=case.get("prohibited_terms", []),
        )
        r4 = evaluate_tone_alignment(brief, case["brand_id"])

        case_passed = r1["passed"] and r2["passed"] and r3["passed"] and r4["passed"]
        if not case_passed:
            all_passed = False

        results.append(
            {
                "test_id": case["test_id"],
                "brand_id": case["brand_id"],
                "category": case["category"],
                "passed": case_passed,
                "rubrics": {
                    "schema_conformance": r1,
                    "grounding_accuracy": r2,
                    "memory_compliance": r3,
                    "tone_alignment": r4,
                },
            }
        )

    summary = {
        "suite": "Antigravity Evaluation Harness",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(results),
        "passed_cases": sum(1 for r in results if r["passed"]),
        "pass_rate": sum(1 for r in results if r["passed"]) / max(len(results), 1),
        "overall_status": "PASSED" if all_passed else "FAILED",
        "results": results,
    }

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Antigravity Evaluation Suite")
    parser.add_argument("--config", default="evals/eval_config.yaml")
    parser.add_argument("--dataset", default="evals/test_dataset.jsonl")
    parser.add_argument("--output", default="evals/results/latest_run.json")
    args = parser.parse_args()

    summary = asyncio.run(run_evaluation_suite(args.dataset, args.output))
    print(json.dumps(summary, indent=2))
    if summary["overall_status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
