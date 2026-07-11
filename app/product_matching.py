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
    "futerał",
    "futeral",
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
    r"\b(?:adapter|bateria|case|cover|etui|folia|futeral|glass|kabel|ladowarka|obudowa|"
    r"pokrowiec|protector|szklo|szybka|uchwyt|wyswietlacz)\b.*\b(?:do|dla|for)\b"
)

# Spare-part nouns that mark a parts listing wherever they appear in the title
# ("Oryginalny wyświetlacz samsung S25 z ramką"). "ł" survives NFKD, so both
# spellings are needed.
_SPARE_PART_ANYWHERE = re.compile(
    r"\b(?:wyswietlacz|wyświetlacz|p[lł]yta g[lł]owna|korpus|digitizer|tasma|taśma)\b"
)

# Variant suffixes that change the product identity (S25 vs S25 FE/Ultra).
FOREIGN_VARIANT_MARKERS = frozenset(
    {"fe", "ultra", "plus", "pro", "max", "mini", "lite", "neo", "edge", "active"}
)


def is_accessory_title(title: str) -> bool:
    ascii_title = "".join(
        character
        for character in unicodedata.normalize("NFKD", title)
        if not unicodedata.combining(character)
    )
    normalized = " ".join(ascii_title.casefold().split())
    return (
        normalized.startswith(ACCESSORY_TITLE_PREFIXES)
        or bool(_ACCESSORY_FOR_PRODUCT.search(normalized))
        or bool(_SPARE_PART_ANYWHERE.search(normalized))
    )


def canonical_product_text(value: str) -> str:
    ascii_value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    ).casefold()
    ascii_value = re.sub(r"generac(?:ja|ji|je)|generation", "gen", ascii_value)
    return re.sub(r"[^a-z0-9]+", "", ascii_value)


def product_words(value: str) -> list[str]:
    ascii_value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    ).casefold()
    ascii_value = re.sub(r"generac(?:ja|ji|je)|generation", "gen", ascii_value)
    # "S25+" is the Plus variant, but a detached "+" ("S25 + etui") is a bundle.
    ascii_value = re.sub(r"(?<=\w)\+", " plus ", ascii_value)
    # Split glued variants ("s25fe", "s25ultra") so markers are separate tokens.
    ascii_value = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", ascii_value)
    return re.findall(r"[a-z0-9]+", ascii_value)


def matches_product_title(title: str, expected_model: str) -> bool:
    expected_words = product_words(expected_model)
    if not expected_words or is_accessory_title(title):
        return False
    title_words = set(product_words(title))
    # Every expected token must appear; extra brand-line words in between are fine
    # ("Samsung S25" matches "Samsung Galaxy S25"). Contiguous match is the fallback
    # for titles glued together without separators.
    if not all(word in title_words for word in expected_words):
        if canonical_product_text(expected_model) not in canonical_product_text(title):
            return False
    return not ((FOREIGN_VARIANT_MARKERS & title_words) - set(expected_words))


def is_direct_olx_listing_url(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return (hostname == "olx.pl" or hostname.endswith(".olx.pl")) and parsed.path.startswith(
        "/d/oferta/"
    )
