import pytest
from pydantic import ValidationError

from app.domain.models import Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion


def suggestion(index: int) -> ProductSuggestion:
    return ProductSuggestion(
        brand="Sony",
        model=f"WF-{index}",
        estimated_used_price_pln=400,
        key_features=["ANC"],
        why_it_fits="Dobre dopasowanie",
        tradeoff="Inny ekosystem",
    )


def test_ready_conversation_requires_four_to_six_suggestions() -> None:
    with pytest.raises(ValidationError):
        ConversationOutput(
            requirements=Requirements(),
            missing_critical_information=False,
            suggestions=[suggestion(1)],
        )


def test_ready_conversation_can_infer_default_flag_from_candidate_list() -> None:
    output = ConversationOutput(
        requirements=Requirements(),
        suggestions=[suggestion(index) for index in range(4)],
    )

    assert output.missing_critical_information is False


def test_clarifying_question_requires_question_and_no_suggestions() -> None:
    with pytest.raises(ValidationError):
        ConversationOutput(
            requirements=Requirements(),
            missing_critical_information=True,
            question=None,
            suggestions=[],
        )

    valid = ConversationOutput(
        requirements=Requirements(),
        missing_critical_information=True,
        question="Jaki masz budżet?",
        suggestions=[],
    )
    assert valid.question == "Jaki masz budżet?"


def test_brand_without_model_is_not_a_reference_product() -> None:
    output = ConversationOutput.model_validate(
        {
            "requirements": {
                "category": "headphones",
                "reference_product": {"brand": "Sony", "model": None},
            },
            "missing_critical_information": True,
            "question": "Jaki jest Twój budżet na słuchawki?",
            "suggestions": [],
            "reference_product": {"brand": "Sony", "model": None},
            "change_intent": None,
        }
    )

    assert output.reference_product is None
    assert output.requirements.reference_product is None
    assert output.change_intent.value == "rerank"
