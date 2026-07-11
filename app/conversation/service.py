import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.domain.models import ChangeIntent, ReferenceProduct, Requirements
from app.llm.schemas import ConversationOutput, ProductSuggestion
from app.services.ports import LLMClient

CONVERSATION_PROMPT_V1 = """Jesteś polskim doradcą zakupowym na całym rynku używanej elektroniki.
Najpierw rozpoznaj kategorię urządzenia z wiadomości użytkownika i zapisz ją jako krótki,
stabilny identyfikator w requirements.category, np. smartphones, laptops, tablets, consoles,
cameras, headphones lub smartwatches. Nie zakładaj kategorii na podstawie poprzedniej wartości
electronics. Aktualizuj pozostałe wymagania na podstawie wiadomości.
Rozpoznaj produkt referencyjny tylko wtedy, gdy użytkownik poda jednoznaczny model produktu
(z marką podaną wprost albo możliwą do pewnego ustalenia) i zachowaj go w kolejnych turach.
Sama marka, np. „słuchawki Sony”, nie jest produktem referencyjnym: w takim przypadku ustaw
reference_product=null zarówno na poziomie głównym, jak i w requirements.
Zadaj najwyżej jedno istotne pytanie, tylko gdy brakuje budżetu lub zastosowania/ważnej cechy.
Pytanie musi wprost dotyczyć rozpoznanej kategorii lub urządzenia użytkownika. Nigdy nie pytaj
o cechy innej kategorii. Przykład: dla Samsung S25 pytaj o budżet na telefon, nie o słuchawki.
Łącznie w sesji wolno zadać najwyżej 3 pytania. Gdy dane wystarczają, zwróć 4–6 konkretnych modeli.
Produkt referencyjny razem z budżetem i co najmniej jedną ważną cechą lub zastosowaniem
jest wystarczającym wejściem: ustaw missing_critical_information=false, question=null
i zwróć 4–6 propozycji. Nie zwracaj new_product_research bez propozycji modeli.
Jeśli użytkownik mówi, że chce kupić konkretny model, traktuj go jako twardy punkt odniesienia.
Pierwsza propozycja ma być dokładnie tym modelem, a pozostałe muszą należeć do tej samej marki
i rodziny produktu. Nie zamieniaj iPhone'a na telefony z Androidem ani odwrotnie, chyba że
użytkownik wprost poprosi o alternatywy innych marek. Budżet niższy od typowej ceny pokaż jako
kompromis lub ryzyko, ale nie używaj go do cichej zmiany wskazanego produktu.
Budżet użytkownika dotyczy cen na rynku wtórnym (używanych), nie cen nowych. Proponuj modele,
których typowa cena używana mieści się w budżecie i dobrze go wykorzystuje — także modele
z wyższej półki, które nowe kosztowały znacznie więcej, a używane są już w zasięgu budżetu.
estimated_used_price_pln podawaj jako realistyczną cenę używanego egzemplarza.
Możesz rozważyć maksymalnie 10 kandydatów, ale zwróć tylko najlepsze propozycje z ceną,
powodami podobieństwa, różnicami i kompromisem.
Nie decyduj o cache, filtrach ani punktacji.
change_intent zawsze ustaw na jedną z wartości: rerank, refetch albo new_product_research;
nigdy nie zwracaj null.
Zachowaj wcześniejsze wymagania, których użytkownik nie zmienił.
Propozycje modeli muszą należeć do rozpoznanej kategorii. Mogą korzystać z ogólnej wiedzy
o produktach, ale nie są ofertami.
Nie wymyślaj URL-i ani faktów o ofertach. source_url ustaw tylko, gdy URL podał użytkownik;
w przeciwnym razie pozostaw null i wpisz unverified_product_suggestion do data_gaps."""


@dataclass(frozen=True)
class ConversationResult:
    requirements: Requirements
    question: str | None
    suggestions: list[ProductSuggestion]
    change_intent: ChangeIntent
    reference_product: ReferenceProduct | None = None


@dataclass(frozen=True)
class DirectProductSearch:
    product: ReferenceProduct
    budget_max: Decimal | None = None


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
        reference_product = (
            _infer_explicit_reference_product(message)
            or output.reference_product
            or current.reference_product
        )
        requirements = output.requirements.model_copy(
            update={
                "question_count": current.question_count,
                "reference_product": reference_product,
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
            reference_product,
        )


_IPHONE_MODEL = re.compile(
    r"\biphone[\s-]*(\d{1,2})(?:[\s-]*(pro(?:[\s-]*max)?|plus|mini|e|s|c))?\b",
    re.IGNORECASE,
)

_DIRECT_LISTING_REQUEST = re.compile(
    r"\b(?:znajdź|wyszukaj|pokaż|szukaj|sprawdź)\s+(?:mi\s+)?"
    r"(?:konkretne\s+)?(?:ogłoszenia|oferty)\s*(?:dla\s+|na\s+)?(?P<product>.+)$",
    re.IGNORECASE,
)
_BUDGET = re.compile(
    r"\s+(?:do|max(?:ymalnie)?|za)\s+(?P<amount>\d[\d\s.,]*)\s*(?:zł|pln)\b.*$",
    re.IGNORECASE,
)


def infer_direct_product_search(message: str) -> DirectProductSearch | None:
    """Recognize only explicit listing commands for a concrete alphanumeric model."""
    match = _DIRECT_LISTING_REQUEST.search(" ".join(message.split()))
    if match is None:
        return None
    product_text = match.group("product").strip(" .,!?:;\"'")
    if len(product_text) > 120:
        return None
    budget_max: Decimal | None = None
    budget_match = _BUDGET.search(product_text)
    if budget_match is not None:
        raw_amount = budget_match.group("amount").replace(" ", "").replace(",", ".")
        try:
            budget_max = Decimal(raw_amount)
        except InvalidOperation:
            return None
        product_text = product_text[: budget_match.start()].strip()
    parts = product_text.split()
    if len(parts) < 2:
        return None
    raw_brand, model_parts = parts[0], parts[1:]
    model = " ".join(model_parts).strip(" .,!?:;\"'")
    if not raw_brand[0].isalpha() or not any(character.isdigit() for character in model):
        return None
    brand = (
        raw_brand
        if any(character.isupper() for character in raw_brand[1:])
        else raw_brand.capitalize()
    )
    return DirectProductSearch(
        product=ReferenceProduct(brand=brand, model=model, confidence=0.99),
        budget_max=budget_max,
    )


def _infer_explicit_reference_product(message: str) -> ReferenceProduct | None:
    match = _IPHONE_MODEL.search(message)
    if match is None:
        return None
    generation, raw_variant = match.groups()
    variant = ""
    if raw_variant:
        normalized_variant = " ".join(raw_variant.lower().replace("-", " ").split())
        variant = {
            "pro": " Pro",
            "pro max": " Pro Max",
            "plus": " Plus",
            "mini": " Mini",
            "e": "e",
            "s": "s",
            "c": "c",
        }[normalized_variant]
    return ReferenceProduct(
        brand="Apple",
        model=f"iPhone {generation}{variant}",
        confidence=0.99,
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
