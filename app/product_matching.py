import re
import unicodedata

ACCESSORY_TITLE_PREFIXES = (
    "adapter",
    "bateria do",
    "case",
    "cover",
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
