from app.reference_data import (
    CATEGORY_ROWS,
    VECTOR_ROWS,
    validate_reference_data,
)


def test_reference_data_sums_to_1000():
    validate_reference_data()

    scored_total = sum(c["points_total"] for c in CATEGORY_ROWS if c["scored"])
    assert scored_total == 1000


def test_vector_budgets_match_category_totals():
    sums = {}
    for v in VECTOR_ROWS:
        sums[v["category_id"]] = sums.get(v["category_id"], 0) + v["points_budget"]

    for cat in CATEGORY_ROWS:
        assert sums.get(cat["id"], 0) == cat["points_total"], cat["key"]
