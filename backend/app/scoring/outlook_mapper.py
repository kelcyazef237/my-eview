"""Trust Outlook momentum mapper."""

from dataclasses import dataclass


DEFAULT_OUTLOOK = {
    5: "Positive · Stable",
    4: "Positive",
    3: "Stable · Improving",
    2: "Stable · Watch",
    1: "Negative · Action Required",
}


@dataclass(frozen=True)
class OutlookResult:
    outlook: str
    delta: int | None
    is_first_full_report: bool


def outlook_for_score(
    current_score: int,
    current_tier: int,
    previous_full_report_score: int | None,
    is_first_full_report: bool = False,
) -> OutlookResult:
    if is_first_full_report:
        return OutlookResult(
            outlook="MYETREND: available after 90 days",
            delta=None,
            is_first_full_report=True,
        )

    default = DEFAULT_OUTLOOK.get(current_tier, "Stable")
    if previous_full_report_score is None:
        return OutlookResult(outlook=default, delta=None, is_first_full_report=False)

    delta = current_score - previous_full_report_score

    if delta >= 20:
        return OutlookResult(outlook="Positive", delta=delta, is_first_full_report=False)

    if delta <= -30:
        if current_tier <= 2:
            return OutlookResult(outlook="Negative · Action Required", delta=delta, is_first_full_report=False)
        return OutlookResult(outlook="Watch", delta=delta, is_first_full_report=False)

    return OutlookResult(outlook=default, delta=delta, is_first_full_report=False)
