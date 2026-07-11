from decimal import Decimal

import pytest

from app.conversation.service import (
    ConversationService,
    classify_change,
    infer_direct_product_search,
)
from app.domain.models import ChangeIntent, Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion


class MockLLM:
    def __init__(self, output: ConversationOutput) -> None:
        self.output = output
        self.calls: list[dict[str, object]] = []

    async def structured_response(self, **kwargs: object) -> ConversationOutput:
        self.calls.append(kwargs)
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


async def test_conversation_starts_neutral_and_infers_electronics_category() -> None:
    output = ConversationOutput(
        requirements=Requirements(category="smartphones"),
        missing_critical_information=True,
        question="Jaki jest Twój maksymalny budżet na telefon?",
        suggestions=[],
    )
    llm = MockLLM(output)

    result = await ConversationService(llm).handle_message(
        "Szukam Samsung S25", Requirements()
    )

    assert Requirements().category == "electronics"
    assert result.requirements.category == "smartphones"
    assert result.question == "Jaki jest Twój maksymalny budżet na telefon?"
    assert "używanej elektroniki" in str(llm.calls[0]["system_prompt"])
    assert "słuchawek" not in str(llm.calls[0]["system_prompt"])


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


@pytest.mark.parametrize(
    ("message", "brand", "model", "budget"),
    [
        ("Znajdź ogłoszenia dla Sony WF-1000XM4", "Sony", "WF-1000XM4", None),
        ("Pokaż mi oferty dla Samsung S25 do 2500 zł", "Samsung", "S25", "2500"),
        ("Wyszukaj ogłoszenia Apple iPhone 15 Pro", "Apple", "iPhone 15 Pro", None),
    ],
)
def test_explicit_listing_command_detects_exact_product_without_llm(
    message: str,
    brand: str,
    model: str,
    budget: str | None,
) -> None:
    result = infer_direct_product_search(message)

    assert result is not None
    assert result.product.brand == brand
    assert result.product.model == model
    actual_budget = str(result.budget_max) if result.budget_max is not None else None
    assert actual_budget == budget


@pytest.mark.parametrize(
    "message",
    [
        "Coś jak AirPods Pro, ale taniej",
        "Szukam słuchawek Sony z ANC",
        "Jakie oferty są najlepsze?",
        "Znajdź ogłoszenia dla słuchawek Sony",
    ],
)
def test_ambiguous_or_comparison_message_does_not_use_direct_search(message: str) -> None:
    assert infer_direct_product_search(message) is None
