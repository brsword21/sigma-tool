from decimal import Decimal

import pytest

from app.conversation.service import ConversationService, classify_change
from app.domain.models import ChangeIntent, Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion


class MockLLM:
    def __init__(self, output: ConversationOutput) -> None:
        self.output = output

    async def structured_response(self, **kwargs: object) -> ConversationOutput:
        return self.output


def suggestions() -> list[ProductSuggestion]:
    return [
        ProductSuggestion(
            brand="Sony",
            model=f"XM{i}",
            estimated_used_price_pln=400,
            key_features=["ANC"],
            why_it_fits="pasuje",
            tradeoff="kompromis",
        )
        for i in range(4)
    ]


async def test_ready_conversation_returns_four_models() -> None:
    requirements = Requirements(budget_max=Decimal("500"), required_features=["ANC"])
    service = ConversationService(
        MockLLM(
            ConversationOutput(
                requirements=requirements,
                missing_critical_information=False,
                suggestions=suggestions(),
            )
        )
    )
    result = await service.handle_message("ANC do 500", Requirements())
    assert len(result.suggestions) == 4
    assert result.question is None


async def test_fourth_question_is_suppressed_and_requires_suggestions() -> None:
    output = ConversationOutput(
        requirements=Requirements(question_count=3),
        missing_critical_information=True,
        question="Jeszcze jedno?",
        suggestions=[],
    )
    with pytest.raises(ValueError, match="4-6"):
        await ConversationService(MockLLM(output)).handle_message(
            "nie wiem", Requirements(question_count=3)
        )


def test_change_classifier_separates_rerank_refetch_and_research() -> None:
    before = Requirements(preferred_colors=["black"])
    assert (
        classify_change(
            before,
            Requirements(preferred_colors=["blue"]),
            cached_fields={"preferred_colors"},
            cache_is_fresh=True,
            cached_filtered_count=8,
        )
        is ChangeIntent.RERANK
    )
    assert (
        classify_change(
            before,
            Requirements(budget_max=Decimal("300")),
            cached_fields={"preferred_colors"},
            cache_is_fresh=True,
            cached_filtered_count=8,
        )
        is ChangeIntent.REFETCH
    )
    assert (
        classify_change(
            before,
            Requirements(category="laptops"),
            cached_fields=set(),
            cache_is_fresh=True,
            cached_filtered_count=8,
        )
        is ChangeIntent.NEW_PRODUCT_RESEARCH
    )
