import json
from dataclasses import dataclass

from app.domain.models import ChangeIntent, ReferenceProduct, Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion
from app.services.ports import LLMClient

CONVERSATION_PROMPT_V1 = """Jesteś polskim doradcą używanych słuchawek.
Aktualizuj wymagania na podstawie wiadomości.
Rozpoznaj produkt referencyjny, jeśli użytkownik poda markę lub model,
i zachowaj go w kolejnych turach.
Zadaj najwyżej jedno istotne pytanie, tylko gdy brakuje budżetu lub zastosowania/ważnej cechy.
Łącznie w sesji wolno zadać najwyżej 3 pytania. Gdy dane wystarczają, zwróć 4–6 konkretnych modeli.
Produkt referencyjny razem z budżetem i co najmniej jedną ważną cechą lub zastosowaniem
jest wystarczającym wejściem: ustaw missing_critical_information=false, question=null
i zwróć 4–6 propozycji. Nie zwracaj new_product_research bez propozycji modeli.
Możesz rozważyć maksymalnie 10 kandydatów, ale zwróć tylko najlepsze propozycje z ceną,
powodami podobieństwa, różnicami i kompromisem.
Nie decyduj o cache, filtrach ani punktacji.
Zachowaj wcześniejsze wymagania, których użytkownik nie zmienił.
Propozycje modeli mogą korzystać z ogólnej wiedzy o produktach, ale nie są ofertami.
Nie wymyślaj URL-i ani faktów o ofertach. source_url ustaw tylko, gdy URL podał użytkownik;
w przeciwnym razie pozostaw null i wpisz unverified_product_suggestion do data_gaps."""


@dataclass(frozen=True)
class ConversationResult:
    requirements: Requirements
    question: str | None
    suggestions: list[ProductSuggestion]
    change_intent: ChangeIntent
    reference_product: ReferenceProduct | None = None


class ConversationService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def handle_message(self, message: str, current: Requirements) -> ConversationResult:
        output = await self._llm.structured_response(
            system_prompt=CONVERSATION_PROMPT_V1,
            user_prompt=json.dumps(
                {"message": message, "current_requirements": current.model_dump(mode="json")},
                ensure_ascii=False,
            ),
            response_model=ConversationOutput,
        )
        requirements = output.requirements.model_copy(
            update={
                "question_count": current.question_count,
                "reference_product": output.reference_product or current.reference_product,
            }
        )
        question = output.question if output.missing_critical_information else None
        suggestions = output.suggestions[:6]
        if question and current.question_count < 3:
            requirements = requirements.model_copy(
                update={"question_count": current.question_count + 1}
            )
            suggestions = []
        else:
            question = None
            if not 4 <= len(suggestions) <= 6:
                raise ValueError("ready conversation output must contain 4-6 product suggestions")
        return ConversationResult(
            requirements,
            question,
            suggestions,
            output.change_intent,
            output.reference_product or current.reference_product,
        )


def classify_change(
    before: Requirements,
    after: Requirements,
    *,
    cached_fields: set[str],
    cache_is_fresh: bool,
    cached_filtered_count: int,
) -> ChangeIntent:
    if before.category != after.category:
        return ChangeIntent.NEW_PRODUCT_RESEARCH
    hard_changed = any(
        getattr(before, field) != getattr(after, field)
        for field in (
            "budget_max",
            "required_variants",
            "required_features",
            "location",
            "delivery_required",
        )
    )
    changed_fields = {
        field
        for field in Requirements.model_fields
        if getattr(before, field) != getattr(after, field)
    }
    if (
        not cache_is_fresh
        or cached_filtered_count < 5
        or (hard_changed and not changed_fields <= cached_fields)
    ):
        return ChangeIntent.REFETCH
    return ChangeIntent.RERANK
