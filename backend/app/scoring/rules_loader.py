from pathlib import Path
from typing import Any

import yaml

from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS, validate_reference_data


DEFAULT_RULESET_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "scoring_rules_v1.yaml"


def load_ruleset(path: Path | str | None = None) -> dict[str, Any]:
    path = Path(path or DEFAULT_RULESET_PATH)
    with path.open("r", encoding="utf-8") as f:
        ruleset = yaml.safe_load(f)
    validate_ruleset(ruleset)
    return ruleset


def validate_ruleset(ruleset: dict[str, Any]) -> None:
    """Validate that YAML ruleset matches the seeded reference data."""
    validate_reference_data()

    cat_rows = {c["key"]: c for c in CATEGORY_ROWS}
    vec_rows = {v["key"]: v for v in VECTOR_ROWS}

    scored_total = 0
    for cat in ruleset.get("categories", []):
        cat_key = cat["key"]
        ref_cat = cat_rows.get(cat_key)
        if not ref_cat:
            raise ValueError(f"Ruleset has unknown category {cat_key}")
        if cat["points_total"] != ref_cat["points_total"]:
            raise ValueError(
                f"Category {cat_key} ruleset total {cat['points_total']} != reference {ref_cat['points_total']}"
            )
        if cat["scored"] != ref_cat["scored"]:
            raise ValueError(f"Category {cat_key} scored flag mismatch")
        if ref_cat["scored"]:
            scored_total += cat["points_total"]

        vector_sum = 0
        for vec in cat.get("vectors", []):
            vec_key = vec["key"]
            ref_vec = vec_rows.get(vec_key)
            if not ref_vec:
                raise ValueError(f"Ruleset has unknown vector {vec_key} in {cat_key}")
            if ref_vec["category_id"] != ref_cat["id"]:
                raise ValueError(f"Vector {vec_key} category mismatch")
            vector_sum += vec["points_budget"]
        if vector_sum != cat["points_total"]:
            raise ValueError(
                f"Category {cat_key} vector budgets sum to {vector_sum}, expected {cat['points_total']}"
            )

    if scored_total != ruleset.get("max_possible_score", 1000):
        raise ValueError(f"Scored category totals {scored_total} != max_possible_score")
