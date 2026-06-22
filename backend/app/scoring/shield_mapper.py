"""Shield tier mapping."""

from dataclasses import dataclass


SHIELD_TIERS = [
    {"tier": 1, "min": 0, "max": 399, "label": "Foundational Digital Trust", "short_label": "Shield I"},
    {"tier": 2, "min": 400, "max": 599, "label": "Developing Digital Trust", "short_label": "Shield II"},
    {"tier": 3, "min": 600, "max": 749, "label": "Above Average Digital Trust", "short_label": "Shield III"},
    {"tier": 4, "min": 750, "max": 899, "label": "Strong Digital Trust", "short_label": "Shield IV"},
    {"tier": 5, "min": 900, "max": 1000, "label": "Exemplary Digital Trust", "short_label": "Shield V"},
]


SHIELD_COLORS = {
    1: {"bg": "#B8200A", "text": "#FFFFFF", "name": "red"},
    2: {"bg": "#9A5200", "text": "#FFFFFF", "name": "amber"},
    3: {"bg": "#1A5C8A", "text": "#FFFFFF", "name": "blue"},
    4: {"bg": "#0F7B7B", "text": "#FFFFFF", "name": "teal"},
    5: {"bg": "#0F5C2E", "text": "#FFFFFF", "name": "green"},
}


@dataclass(frozen=True)
class ShieldResult:
    tier: int
    label: str
    short_label: str
    band: str
    color: dict


def shield_for_score(score: int) -> ShieldResult:
    score = max(0, min(1000, score))
    for s in SHIELD_TIERS:
        if s["min"] <= score <= s["max"]:
            return ShieldResult(
                tier=s["tier"],
                label=s["label"],
                short_label=s["short_label"],
                band=s["label"],
                color=SHIELD_COLORS[s["tier"]],
            )
    # Fallback should not happen because ranges cover 0-1000.
    return ShieldResult(tier=1, label="Shield I", short_label="Shield I", band="Foundational Digital Trust", color=SHIELD_COLORS[1])
