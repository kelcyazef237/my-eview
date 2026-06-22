from app.reference_data import validate_reference_data
from app.scoring.rules_loader import validate_ruleset, load_ruleset


def validate_all(ruleset_path: str | None = None) -> None:
    """Validate reference data and loaded ruleset."""
    validate_reference_data()
    ruleset = load_ruleset(ruleset_path)
    validate_ruleset(ruleset)
