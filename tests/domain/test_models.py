from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.models import ScoreBreakdown, SearchQuery


def test_search_query_rejects_empty_model() -> None:
    with pytest.raises(ValidationError):
        SearchQuery(model="")


def test_score_breakdown_caps_total_at_zero() -> None:
    breakdown = ScoreBreakdown(
        price=Decimal("0"),
        requirements=Decimal("0"),
        condition=Decimal("0"),
        completeness=Decimal("0"),
        logistics=Decimal("0"),
        preferences=Decimal("0"),
        risk_penalty=Decimal("30"),
    )

    assert breakdown.total == 0
