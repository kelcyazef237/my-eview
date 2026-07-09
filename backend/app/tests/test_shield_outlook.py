import pytest

from app.scoring.shield_mapper import shield_for_score
from app.scoring.outlook_mapper import outlook_for_score


@pytest.mark.parametrize(
    "score,expected_tier",
    [
        (0, 1),
        (399, 1),
        (400, 2),
        (599, 2),
        (600, 3),
        (749, 3),
        (750, 4),
        (899, 4),
        (900, 5),
        (1000, 5),
    ],
)
def test_shield_boundaries(score, expected_tier):
    result = shield_for_score(score)
    assert result.tier == expected_tier


def test_outlook_first_full_report():
    result = outlook_for_score(850, 4, None, is_first_full_report=True)
    assert result.outlook == "MYETREND: available after 90 days"


def test_outlook_positive_momentum():
    result = outlook_for_score(820, 4, 800, is_first_full_report=False)
    assert result.outlook == "Positive"


def test_outlook_negative_momentum_high_tier():
    result = outlook_for_score(820, 4, 860, is_first_full_report=False)
    assert result.outlook == "Watch"


def test_outlook_negative_momentum_low_tier():
    result = outlook_for_score(450, 2, 500, is_first_full_report=False)
    assert result.outlook == "Negative · Action Required"


def test_outlook_default_by_tier():
    assert outlook_for_score(950, 5, 945).outlook == "Positive · Stable"
    assert outlook_for_score(850, 4, 845).outlook == "Positive"
    assert outlook_for_score(700, 3, 695).outlook == "Stable · Improving"
    assert outlook_for_score(500, 2, 495).outlook == "Stable · Watch"
    assert outlook_for_score(300, 1, 295).outlook == "Negative · Action Required"
