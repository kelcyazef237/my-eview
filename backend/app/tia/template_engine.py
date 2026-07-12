"""Deterministic Trust Impact Analysis template engine."""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, BaseLoader

from app.constants import VectorState, REGULATORY_DISCLAIMER
from app.sector_config import tia_regulatory_text, sector_label


DEFAULT_TEMPLATES_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "tia_templates_v1.yaml"


class TemplateEngine:
    def __init__(self, path: Path | str | None = None):
        path = Path(path or DEFAULT_TEMPLATES_PATH)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.version = data.get("version", "v1")
        self.templates = data.get("templates", {})
        self.env = Environment(loader=BaseLoader())

    def _has_material_findings(self, category_key: str, vector_states: dict[str, dict]) -> bool:
        cat = self.templates.get(category_key)
        if not cat:
            return False
        for vec_key, finding in vector_states.items():
            if vec_key in cat.get("vectors", []) and finding.get("state") in ("WARN", "FAIL"):
                return True
        return False

    def _build_context(
        self,
        org_name: str,
        domain: str,
        vector_states: dict[str, dict],
        sector: str | None = None,
    ) -> dict[str, Any]:
        ctx = {
            "org_name": org_name,
            "domain": domain,
            "sector": sector or "general",
            "sector_label": sector_label(sector),
            "sector_regulations": tia_regulatory_text(sector),
            "regulatory_disclaimer": REGULATORY_DISCLAIMER,
        }
        for vec_key, finding in vector_states.items():
            ctx[vec_key] = finding.get("state", "NOT_OBSERVED")
            ctx[f"{vec_key}_meta"] = finding.get("meta") or {}
        return ctx

    def render_category(
        self,
        category_key: str,
        org_name: str,
        domain: str,
        vector_states: dict[str, dict],
        sector: str | None = None,
    ) -> dict[str, Any]:
        cat_templates = self.templates.get(category_key)
        if not cat_templates:
            return {
                "template_id": f"{category_key}_missing_v1",
                "rendered_text": {
                    "technical_observation": "No TIA template available for this category.",
                    "business_impact": "",
                    "stakeholders_affected": [],
                    "regulatory_relevance": "",
                    "recommended_action": "",
                },
            }

        variant = "dirty" if self._has_material_findings(category_key, vector_states) else "clean"
        template = cat_templates.get(variant, cat_templates.get("dirty", {}))
        template_id = template.get("template_id", f"{category_key}_{variant}_v1")

        ctx = self._build_context(org_name, domain, vector_states, sector)
        rendered = {}
        for slot in ("technical_observation", "business_impact", "stakeholders_affected", "regulatory_relevance", "recommended_action"):
            raw = template.get(slot, "")
            if isinstance(raw, str):
                t = self.env.from_string(raw)
                rendered[slot] = t.render(ctx).strip()
            else:
                rendered[slot] = raw

        return {
            "template_id": template_id,
            "rendered_text": rendered,
        }

    def render_all(
        self,
        org_name: str,
        domain: str,
        category_vector_states: dict[str, dict[str, dict]],
        sector: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        return {
            cat_key: self.render_category(cat_key, org_name, domain, states, sector)
            for cat_key, states in category_vector_states.items()
        }
