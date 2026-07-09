"""Report rendering pipeline: Jinja2 HTML + WeasyPrint PDF."""

import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.urls import default_url_fetcher

from app.models.category_score import CategoryScore
from app.models.organization import Organization
from app.models.score import Score
from app.models.score_history import ScoreHistory
from app.models.tia_entry import TiaEntry
from app.models.vector_finding import VectorFinding
from app.scoring.shield_mapper import shield_for_score

logger = logging.getLogger("myeview.reports")


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


# External resources (Google Fonts) are fetched with a short socket timeout so a
# blocked/hanging connection can't stall PDF generation for tens of seconds. On
# failure WeasyPrint logs a warning and falls back to system fonts — the PDF
# still renders, just with a substitute typeface.
def _timed_url_fetcher(url, timeout=3, ssl_context=None, http_headers=None, allowed_protocols=None):
    return default_url_fetcher(
        url,
        timeout=timeout,
        ssl_context=ssl_context,
        http_headers=http_headers,
        allowed_protocols=allowed_protocols,
    )


def _severity_for_category(points_lost: int, points_total: int) -> str:
    if points_total == 0:
        return "low"
    ratio = points_lost / points_total
    if ratio >= 0.4:
        return "critical"
    if ratio >= 0.2:
        return "high"
    if ratio >= 0.05:
        return "medium"
    return "low"


def _benchmark_percentile(score: int) -> dict[str, float]:
    """Placeholder benchmark percentiles until real benchmark data is available."""
    # Sigmoid-style mapping so score 500 ≈ 50%, 900 ≈ 95%.
    import math
    sector = 100 / (1 + math.exp(-0.01 * (score - 500)))
    national = min(99.9, sector * 1.05)
    return {
        "sector": round(sector, 2),
        "national": round(national, 2),
    }


def _entity_counts(vectors: list[VectorFinding]) -> dict[str, int]:
    """Derive simple entity-intelligence counts from vector findings."""
    # In a full implementation these would come from dedicated entity-intelligence
    # collectors. For the MVP we surface deterministic counts derived from vectors.
    asset_vectors = {"asset_count", "shadow_assets", "unmanaged_assets"}
    infra_vectors = {"tls_version", "certificate_health", "security_headers", "https_enforcement"}
    threat_vectors = {"malware", "phishing", "spam_blacklist", "botnet", "blacklist_aggregate"}

    asset_fail = sum(1 for v in vectors if v.vector.key in asset_vectors and v.state in ("WARN", "FAIL"))
    infra_fail = sum(1 for v in vectors if v.vector.key in infra_vectors and v.state in ("WARN", "FAIL"))
    threat_fail = sum(1 for v in vectors if v.vector.key in threat_vectors and v.state in ("WARN", "FAIL"))

    return {
        "associated_assets": max(1, len([v for v in vectors if v.vector.key == "asset_count"])),
        "service_dependencies": max(1, infra_fail + 1),
        "risk_related_entities": asset_fail,
        "suspicious_relationships": threat_fail,
    }


def _hygiene_observations(vectors: list[VectorFinding]) -> list[dict[str, Any]]:
    """Build deterministic hygiene observations from vector findings."""
    findings = {v.vector.key: v.state for v in vectors}

    def status(state: str | None) -> str:
        if state == "PASS":
            return "ok"
        if state in ("WARN", "FAIL"):
            return "warn"
        return "info"

    return [
        {
            "title": "HTTPS Enforcement",
            "description": "All observed assets redirect to HTTPS.",
            "status": status(findings.get("https_enforcement")),
        },
        {
            "title": "Security Headers",
            "description": "Critical security headers present on observed responses.",
            "status": status(findings.get("security_headers")),
        },
        {
            "title": "TLS Version",
            "description": "Modern TLS protocol observed; no legacy SSL/TLS.",
            "status": status(findings.get("tls_version")),
        },
        {
            "title": "Exposed Admin Interfaces",
            "description": "No sensitive admin paths observed externally.",
            "status": status(findings.get("exposed_admin")),
        },
        {
            "title": "Email Authentication",
            "description": "SPF, DKIM, and DMARC records configured.",
            "status": status(findings.get("dmarc_enforcement")),
        },
        {
            "title": "DNSSEC Adoption",
            "description": "Domain DNSSEC signatures validated where applicable.",
            "status": status(findings.get("dnssec_adoption")),
        },
    ]


def build_report_context(
    org: Organization,
    score: Score,
    category_scores: list[CategoryScore],
    tia_entries: list[TiaEntry],
    vectors: list[VectorFinding],
    history: list[ScoreHistory],
    previous_full_score: int | None = None,
) -> dict[str, Any]:
    shield = shield_for_score(score.overall_score)
    benchmarks = _benchmark_percentile(score.overall_score)

    # Sort categories by lost points descending to surface priority risks first.
    scored_categories = [
        {
            "key": cs.category.key,
            "name": cs.category.name,
            "parent_group": cs.category.parent_group,
            "points_total": cs.category.points_total,
            "points_lost": cs.points_lost,
            "points_remaining": cs.points_remaining,
            "severity": _severity_for_category(cs.points_lost, cs.category.points_total),
        }
        for cs in category_scores
        if cs.category.scored
    ]
    scored_categories.sort(key=lambda c: c["points_lost"], reverse=True)

    # TIA entries keyed by category key.
    tia_by_category: dict[str, dict[str, Any]] = {}
    for te in tia_entries:
        tia_by_category[te.category.key] = {
            "template_id": te.template_id,
            "rendered_text": te.rendered_text,
        }

    # Risk factors: categories with material deductions paired with their TIA.
    risk_factors = [
        {
            **cat,
            "tia": tia_by_category.get(cat["key"], {}),
        }
        for cat in scored_categories
        if cat["points_lost"] > 0
    ]

    # Clean categories (no deductions) — used for positive signals.
    clean_categories = [cat for cat in scored_categories if cat["points_lost"] == 0]

    return {
        "org": {
            "id": str(org.id),
            "name": org.name,
            "domain": org.primary_domain,
        },
        "score": {
            "overall": score.overall_score,
            "tier": score.shield_tier,
            "shield_label": shield.short_label,
            "outlook": score.outlook,
            "computed_at": score.computed_at,
            "is_full_report": score.is_full_report,
            "previous_full_score": previous_full_score,
        },
        "benchmarks": benchmarks,
        "risk_factors": risk_factors,
        "clean_categories": clean_categories,
        "hygiene": _hygiene_observations(vectors),
        "entity_counts": _entity_counts(vectors),
        "history": [
            {
                "computed_at": h.computed_at,
                "overall_score": h.overall_score,
                "is_full_report": h.is_full_report,
            }
            for h in sorted(history, key=lambda x: x.computed_at)
        ],
    }


def render_html(context: dict[str, Any]) -> str:
    template = env.get_template("report_v1.html.j2")
    return template.render(context)


def merge_ai_into_context(base: dict[str, Any], ai: dict[str, Any]) -> dict[str, Any]:
    """Produce a template-ready context that uses the AI's assessment.

    The rule-based `base` context supplies structural data the AI doesn't
    produce (points, benchmarks, entity counts, history, shield_label).
    The AI `ai` dict supplies the judgment layer: tier, outlook, risk
    narratives, hygiene observations, executive summary, conclusion.

    The risk_factors from the AI are merged onto the base risk_factors
    (which carry points_total/points_lost) so the template still has the
    scoring scaffolding but shows the AI's TIA narrative instead of the
    rule-based template text.
    """
    ctx = dict(base)  # shallow copy — we override specific keys

    score = dict(base["score"])
    score["overall"] = int(ai.get("overall_score", score["overall"]))
    ai_tier = ai.get("shield_tier")
    if isinstance(ai_tier, (int, float)) and 1 <= int(ai_tier) <= 5:
        score["tier"] = int(ai_tier)
        shield = shield_for_score(score["overall"])
        score["shield_label"] = shield.short_label
    if ai.get("outlook"):
        score["outlook"] = ai["outlook"]
    ctx["score"] = score
    ctx["is_ai_report"] = True

    # Index AI risk factors by category key so we can merge narratives
    # onto the base risk factors (which carry points).
    ai_risks = {r.get("key"): r for r in ai.get("risk_factors", []) if r.get("key")}
    merged_risks = []
    for rf in base.get("risk_factors", []):
        ai_rf = ai_risks.get(rf["key"])
        if ai_rf:
            tia = ai_rf.get("tia", {})
            merged_risks.append({
                **rf,
                "severity": ai_rf.get("severity", rf["severity"]),
                "tia": {"rendered_text": tia},
            })
        else:
            merged_risks.append(rf)
    # Also include AI risk factors that don't have a matching base entry
    # (the model may flag something the rules missed).
    existing_keys = {rf["key"] for rf in merged_risks}
    for key, ai_rf in ai_risks.items():
        if key not in existing_keys:
            tia = ai_rf.get("tia", {})
            merged_risks.append({
                "key": key,
                "name": ai_rf.get("name", key),
                "parent_group": ai_rf.get("parent_group", ""),
                "points_total": 0,
                "points_lost": 0,
                "points_remaining": 0,
                "severity": ai_rf.get("severity", "medium"),
                "tia": {"rendered_text": tia},
            })
    ctx["risk_factors"] = merged_risks

    if ai.get("hygiene"):
        ctx["hygiene"] = ai["hygiene"]

    ctx["ai_executive_summary"] = ai.get("executive_summary")
    ctx["ai_conclusion"] = ai.get("conclusion")
    return ctx


def render_pdf(context: dict[str, Any]) -> bytes:
    html = render_html(context)
    try:
        return HTML(string=html, url_fetcher=_timed_url_fetcher).write_pdf()
    except Exception:
        logger.exception("WeasyPrint PDF rendering failed")
        raise
