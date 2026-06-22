from datetime import datetime, timezone

from app.reports.render import render_html, render_pdf


def _minimal_context():
    return {
        "org": {"name": "BACCCUL", "domain": "bacccul.cm"},
        "score": {
            "overall": 860,
            "tier": 3,
            "shield_label": "Shield III",
            "outlook": "Positive",
            "computed_at": datetime.now(timezone.utc),
            "is_full_report": True,
            "previous_full_score": None,
        },
        "benchmarks": {"sector": 88.73, "national": 91.14},
        "risk_factors": [],
        "clean_categories": [],
        "hygiene": [],
        "entity_counts": {
            "associated_assets": 4,
            "service_dependencies": 2,
            "risk_related_entities": 0,
            "suspicious_relationships": 0,
        },
        "history": [],
    }


def test_render_html_not_empty():
    html = render_html(_minimal_context())
    assert html
    assert "BACCCUL" in html
    assert "Myescore" in html


def test_render_pdf_not_empty():
    pdf = render_pdf(_minimal_context())
    assert pdf
    assert pdf.startswith(b"%PDF")
