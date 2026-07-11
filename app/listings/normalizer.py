import re
import unicodedata
from decimal import Decimal, InvalidOperation

from app.domain.models import Currency, ListingCondition, NormalizedListing, RawListing

_PRICE_RE = re.compile(r"(\d[\d\s.,]*)\s*(zł|pln|eur|€|usd|\$)?", re.IGNORECASE)


def normalize_listing(raw: RawListing) -> NormalizedListing:
    price, currency = _parse_price(raw.price_text or str(raw.attributes.get("price", "")))
    text = " ".join([raw.title, raw.description or "", str(raw.attributes)]).casefold()
    return NormalizedListing(
        source=raw.source,
        external_id=raw.external_id,
        url=raw.url,
        title=raw.title,
        price=price,
        currency=currency,
        condition=_condition(text),
        color=_value(raw.attributes, "color", "kolor") or _color(text),
        location=_value(raw.attributes, "location", "lokalizacja", "city"),
        delivery=_delivery(raw.attributes, text),
        exact_variant=_value(raw.attributes, "variant", "wariant", "version", "wersja"),
        warranty=_value(raw.attributes, "warranty", "gwarancja"),
        returns=_value(raw.attributes, "returns", "return", "zwrot"),
        seller_signals={
            key: value
            for key, value in raw.attributes.items()
            if _ascii(str(key)).casefold()
            in {"seller_rating", "seller_reviews", "ocena_sprzedawcy", "liczba_opinii"}
        },
        description=raw.description,
        attributes=raw.attributes,
        image_urls=raw.image_urls,
        raw_payload=raw.raw_payload,
        confidence=0.8 if raw.description and raw.image_urls else 0.6,
        data_gaps=_data_gaps(raw),
    )


def _data_gaps(raw: RawListing) -> list[str]:
    attributes = {_ascii(str(key)).casefold() for key in raw.attributes}
    gaps: list[str] = []
    if not raw.image_urls:
        gaps.append("images")
    if not raw.description:
        gaps.append("description")
    if not attributes & {"warranty", "gwarancja"}:
        gaps.append("warranty")
    if not attributes & {"returns", "return", "zwrot"}:
        gaps.append("returns")
    if not attributes & {"seller_rating", "ocena_sprzedawcy"}:
        gaps.append("seller_signals")
    if not attributes & {"seller_reviews", "liczba_opinii"}:
        gaps.append("seller_reviews")
    if not attributes & {"battery", "bateria", "battery_health", "kondycja_baterii"}:
        gaps.append("battery")
    if not attributes & {"authenticity", "oryginalnosc", "dowod_zakupu"}:
        gaps.append("authenticity")
    return gaps


def _parse_price(value: str) -> tuple[Decimal, Currency]:
    match = _PRICE_RE.search(value.replace("\u00a0", " "))
    if not match:
        raise ValueError("listing price is missing or invalid")
    number = match.group(1).replace(" ", "")
    if "," in number and "." in number:
        number = number.replace(".", "").replace(",", ".")
    elif "," in number:
        number = number.replace(",", ".")
    try:
        price = Decimal(number)
    except InvalidOperation as exc:
        raise ValueError("listing price is missing or invalid") from exc
    symbol = (match.group(2) or "PLN").casefold()
    currency = (
        Currency.EUR
        if symbol in {"eur", "€"}
        else Currency.USD
        if symbol in {"usd", "$"}
        else Currency.PLN
    )
    return price.quantize(Decimal("0.01")), currency


def _value(attributes: dict[str, object], *keys: str) -> str | None:
    normalized = {_ascii(str(key)).casefold(): value for key, value in attributes.items()}
    for key in keys:
        value = normalized.get(_ascii(key).casefold())
        if value not in (None, ""):
            return str(value).strip()
    return None


def _ascii(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))


def _condition(text: str) -> ListingCondition:
    rules = (
        ("jak now", ListingCondition.LIKE_NEW),
        ("idealn", ListingCondition.LIKE_NEW),
        ("bardzo dobr", ListingCondition.VERY_GOOD),
        ("dobr", ListingCondition.GOOD),
        ("używan", ListingCondition.GOOD),
        ("uzywan", ListingCondition.GOOD),
        ("now", ListingCondition.NEW),
        ("uszkodz", ListingCondition.FAIR),
    )
    return next(
        (condition for phrase, condition in rules if phrase in text), ListingCondition.UNKNOWN
    )


def _color(text: str) -> str | None:
    colors = {
        "niebiesk": "blue",
        "blue": "blue",
        "czarn": "black",
        "black": "black",
        "biał": "white",
        "bial": "white",
        "white": "white",
        "srebr": "silver",
    }
    return next((value for phrase, value in colors.items() if phrase in text), None)


def _delivery(attributes: dict[str, object], text: str) -> bool | None:
    value = _value(attributes, "delivery", "dostawa", "przesyłka")
    if value is not None:
        return value.casefold() in {"true", "1", "yes", "tak", "dostępna", "dostepna"}
    if any(word in text for word in ("wysyłka", "wysylka", "przesyłka", "przesylka")):
        return True
    return None
