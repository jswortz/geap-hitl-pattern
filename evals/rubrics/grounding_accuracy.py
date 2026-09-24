"""Rubric 2: Grounding & Citation Accuracy (PRD Section 13.3)."""

from typing import Any, Dict, Iterable
from urllib.parse import urlparse


def evaluate_grounding_accuracy(
    brief_dict: Dict[str, Any], verified_urls: Iterable[str]
) -> Dict[str, Any]:
    """Verify 100% of citations match verified grounding domains with 0% hallucinated links."""
    citations = brief_dict.get("citations", [])
    if not citations:
        return {"passed": False, "score": 0.0, "hallucinated_urls": ["<no_citations>"]}

    verified_list = list(verified_urls)
    verified_set = set(verified_list)
    verified_domains = {urlparse(u).netloc.lower() for u in verified_list if u}

    matched = 0
    hallucinated = []
    for cit in citations:
        url = cit.get("url", "")
        domain = urlparse(url).netloc.lower()
        if url in verified_set or (domain and domain in verified_domains):
            matched += 1
        else:
            hallucinated.append(url)

    score = matched / len(citations)
    return {
        "passed": score == 1.0 and len(hallucinated) == 0,
        "score": score,
        "verified_count": matched,
        "total_citations": len(citations),
        "hallucinated_urls": hallucinated,
    }
