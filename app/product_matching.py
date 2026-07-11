import re
import unicodedata
from urllib.parse import urlparse

ACCESSORY_TITLE_PREFIXES = (
    "adapter",
    "bateria do",
    "case",
    "cover",
    "comply",
    "części do",
    "czesci do",
    "ekran do",
    "etui",
    "folia",
    "glass",
    "kabel",
    "ładowarka",
    "ladowarka",
    "obudowa",
    "pudełko do",
    "pudelko do",
    "pokrowiec",
    "protector",
    "przejściówka",
    "przejsciowka",
    "szkło",
    "szklo",
    "szybka",
    "uchwyt",
    "wyświetlacz do",
    "wyswietlacz do",
)

_ACCESSORY_FOR_PRODUCT = re.compile(
    r"\b(?:adapter|bateria|case|cover|etui|folia|glass|kabel|ladowarka|obudowa|"
    r"pokrowiec|protector|szklo|szybka|uchwyt|wyswietlacz)\b.*\b(?:do|dla|for)\b"
)


def is_accessory_title(title: str) -> bool:
    ascii_title = "".join(
        character
        for character in unicodedata.normalize("NFKD", title)
        if not unicodedata.combining(character)
    )
    normalized = " ".join(ascii_title.casefold().split())
    return normalized.startswith(ACCESSORY_TITLE_PREFIXES) or bool(
        _ACCESSORY_FOR_PRODUCT.search(normalized)
    )


def canonical_product_text(value: str) -> str:
    ascii_value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    ).casefold()
    ascii_value = re.sub(r"generac(?:ja|ji|je)|generation", "gen", ascii_value)
    return re.sub(r"[^a-z0-9]+", "", ascii_value)


def matches_product_title(title: str, expected_model: str) -> bool:
    expected = canonical_product_text(expected_model)
    return bool(
        expected
        and not is_accessory_title(title)
        and expected in canonical_product_text(title)
    )


def is_direct_olx_listing_url(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return (hostname == "olx.pl" or hostname.endswith(".olx.pl")) and parsed.path.startswith(
        "/d/oferta/"
    )
