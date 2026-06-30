"""Pure, deterministic scoring engine."""

from dataclasses import dataclass
from typing import Any

from app.constants import VectorState
from app.scoring.rules_loader import load_ruleset


@dataclass(frozen=True)
class ScoreResult:
    overall_score: int
    category_scores: dict[str, dict[str, Any]]
    is_complete: bool
    not_observed_ratio: float
    not_observed_count: int
    scored_vector_count: int


def _coerce_meta(meta: Any) -> dict[str, Any]:
    """Coerce a finding's ``meta`` value into a dict.

    Findings are persisted via ``VectorFinding.evidence_ref`` (a String column),
    so a round-trip through the DB can leave ``meta`` as a stringified dict
    (either JSON or Python repr). Parse those back into a dict; anything that
    fails to parse becomes an empty dict so meta-based matching degrades
    gracefully instead of crashing.
    """
    if isinstance(meta, dict):
        return meta
    if not meta:
        return {}
    if isinstance(meta, str):
        import json
        try:
            parsed = json.loads(meta)
            return parsed if isinstance(parsed, dict) else {}
        except (ValueError, TypeError):
            pass
        # Fallback: Python repr dicts use single quotes — json can't parse those.
        try:
            import ast
            parsed = ast.literal_eval(meta)
            return parsed if isinstance(parsed, dict) else {}
        except (ValueError, SyntaxError, TypeError):
            pass
    return {}


def _eval_match(match: str | bool, state: str, meta: dict[str, Any]) -> bool:
    """Evaluate a simple match expression.

    Supports:
      - state == VALUE
      - meta.key == value
      - true
    """
    if isinstance(match, bool):
        return match
    match = str(match).strip()
    if match == "true":
        return True

    # Defensive: callers may hand us a non-dict meta (e.g. a stringified dict
    # read back from the DB). Coerce so meta-based matching never crashes.
    if not isinstance(meta, dict):
        meta = _coerce_meta(meta)

    if "==" in match:
        left, right = match.split("==", 1)
        left = left.strip()
        right = right.strip()

        if left == "state":
            return state == right.upper()
        if left.startswith("meta."):
            key = left[5:]
            meta_value = str(meta.get(key, "")).lower()
            return meta_value == right.lower()

    if "!=" in match:
        left, right = match.split("!=", 1)
        left = left.strip()
        right = right.strip()
        if left == "state":
            return state != right.upper()
        if left.startswith("meta."):
            key = left[5:]
            meta_value = str(meta.get(key, "")).lower()
            return meta_value != right.lower()

    return False


def _deduction_for_vector(vector_rules: dict[str, Any], finding: dict[str, Any] | None) -> int:
    if finding is None:
        # No finding at all is treated as NOT_OBSERVED (zero deduction).
        return 0
    state = (finding.get("state") or "NOT_OBSERVED").upper()
    meta = finding.get("meta") or {}

    # NOT_OBSERVED and NOT_APPLICABLE never contribute a deduction.
    # This is critical: without this guard, vectors that use meta-based matching
    # (e.g. DMARC) would fall through to the `match: true` fallback and get scored
    # as FAIL when the check couldn't run — violating the spec's requirement that
    # NOT_OBSERVED is never silently scored as pass or fail.
    if state in (VectorState.NOT_OBSERVED.value, VectorState.NOT_APPLICABLE.value):
        return 0

    for tier in vector_rules.get("tiers", []):
        if _eval_match(tier["match"], state, meta):
            return tier["deduction"]
    return 0


def score_run(findings: dict[str, dict[str, Any]], ruleset: dict[str, Any] | None = None) -> ScoreResult:
    """Pure scoring function.

    findings: {vector_key: {"state": "PASS|WARN|FAIL|...", "meta": {...}}}
    ruleset: loaded ruleset dict; defaults to v1.
    """
    ruleset = ruleset or load_ruleset()

    # Build lookup of vector rules keyed by vector key.
    vector_rules_by_key: dict[str, dict[str, Any]] = {}
    category_by_key: dict[str, dict[str, Any]] = {}
    for cat in ruleset["categories"]:
        category_by_key[cat["key"]] = cat
        for vec in cat.get("vectors", []):
            vector_rules_by_key[vec["key"]] = vec

    scored_vector_count = 0
    not_observed_count = 0
    category_deductions: dict[str, int] = {cat["key"]: 0 for cat in ruleset["categories"]}

    for cat in ruleset["categories"]:
        if not cat.get("scored"):
            continue
        for vec in cat.get("vectors", []):
            scored_vector_count += 1
            vec_key = vec["key"]
            finding = findings.get(vec_key)
            if finding and (finding.get("state") or "NOT_OBSERVED").upper() == VectorState.NOT_OBSERVED.value:
                not_observed_count += 1
            deduction = _deduction_for_vector(vec, finding)
            category_deductions[cat["key"]] += deduction

    category_scores: dict[str, dict[str, Any]] = {}
    overall_score = 0
    for cat in ruleset["categories"]:
        if not cat.get("scored"):
            continue
        total = cat["points_total"]
        lost = max(0, min(abs(category_deductions[cat["key"]]), total))  # cap per category
        remaining = total - lost
        category_scores[cat["key"]] = {
            "category_key": cat["key"],
            "category_name": cat["name"],
            "points_total": total,
            "points_lost": lost,
            "points_remaining": remaining,
        }
        overall_score += remaining

    threshold = ruleset.get("incomplete_threshold_ratio", 0.15)
    not_observed_ratio = not_observed_count / scored_vector_count if scored_vector_count else 0.0
    is_complete = not_observed_ratio <= threshold

    return ScoreResult(
        overall_score=overall_score,
        category_scores=category_scores,
        is_complete=is_complete,
        not_observed_ratio=not_observed_ratio,
        not_observed_count=not_observed_count,
        scored_vector_count=scored_vector_count,
    )
