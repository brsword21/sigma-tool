from app.conversation.service import ConversationService
from app.domain.models import ReferenceProduct, Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion


class MockLLM:
    async def structured_response(self, **kwargs: object) -> ConversationOutput:
        reference = ReferenceProduct(brand="Apple", model="AirPods Pro", confidence=0.95)
        return ConversationOutput(
            requirements=Requirements(required_features=["ANC"]),
            missing_critical_information=False,
            reference_product=reference,
            suggestions=[
                ProductSuggestion(
                    brand="Sony",
                    model=f"WF-{index}",
                    estimated_used_price_pln=350 + index,
                    key_features=["ANC"],
                    similarity_reasons=["dokanalowe", "ANC"],
                    differences=["brak integracji Apple"],
                    why_it_fits="Tańsza alternatywa z ANC",
                    tradeoff="Inny ekosystem",
                    confidence=0.8,
                )
                for index in range(7)
            ],
        )


async def test_reference_product_is_preserved_and_candidate_pool_is_trimmed() -> None:
    result = await ConversationService(MockLLM()).handle_message(
        "coś jak AirPods Pro, ale taniej", Requirements()
    )

    assert result.reference_product is not None
    assert result.reference_product.model == "AirPods Pro"
    assert result.requirements.reference_product == result.reference_product
    assert len(result.suggestions) == 6
    assert result.suggestions[0].similarity_reasons == ["dokanalowe", "ANC"]
