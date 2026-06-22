from app.constants import STAKEHOLDER_TAGS
from app.tia.template_engine import TemplateEngine


def _state(state: str, meta: dict | None = None) -> dict:
    return {"state": state, "meta": meta or {}}


def test_email_dirty_dmarc_none():
    engine = TemplateEngine()
    states = {
        "spf_presence": _state("PASS"),
        "dkim_presence": _state("PASS"),
        "dmarc_enforcement": _state("WARN", {"dmarc_policy": "none"}),
    }
    result = engine.render_category("email_trust", "BACCCUL", "bacccul.cm", states)
    text = " ".join(
        str(value) for value in result["rendered_text"].values()
    )
    assert "DMARC" in text or "monitoring mode" in text
    assert "points" not in text.lower()
    assert "score" not in text.lower()
    assert all(s in STAKEHOLDER_TAGS for s in result["rendered_text"]["stakeholders_affected"])
    assert result["rendered_text"]["regulatory_relevance"].endswith(
        "Regulatory determinations require qualified legal and compliance advisors. "
        "MYEVIEW identifies external exposure signals that may indicate areas warranting compliance review."
    )


def test_email_clean():
    engine = TemplateEngine()
    states = {
        "spf_presence": _state("PASS"),
        "dkim_presence": _state("PASS"),
        "dmarc_enforcement": _state("PASS", {"dmarc_policy": "reject"}),
    }
    result = engine.render_category("email_trust", "BACCCUL", "bacccul.cm", states)
    assert result["template_id"] == "email_trust_clean_v1"
    assert "configured" in result["rendered_text"]["technical_observation"].lower()


def test_tia_determinism():
    engine = TemplateEngine()
    states = {
        "spf_presence": _state("FAIL"),
        "dkim_presence": _state("PASS"),
        "dmarc_enforcement": _state("FAIL", {"dmarc_policy": "absent"}),
    }
    r1 = engine.render_category("email_trust", "BACCCUL", "bacccul.cm", states)
    r2 = engine.render_category("email_trust", "BACCCUL", "bacccul.cm", states)
    assert r1 == r2
