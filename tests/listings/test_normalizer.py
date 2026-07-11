from decimal import Decimal

from app.domain.models import Currency, ListingCondition, RawListing
from app.listings.normalizer import normalize_listing


def test_normalizes_polish_olx_listing() -> None:
    raw = RawListing(
        source="olx_firecrawl",
        external_id="abc",
        url="https://www.olx.pl/d/oferta/abc",
        title="Sony WH-1000XM4 niebieskie",
        price_text="449,99 zł",
        description="Stan bardzo dobry, dostępna wysyłka. Słuchawki działają bez zarzutu.",
        attributes={"Lokalizacja": "Warszawa", "Dostawa": "tak"},
    )
    listing = normalize_listing(raw)
    assert listing.price == Decimal("449.99")
    assert listing.currency is Currency.PLN
    assert listing.condition is ListingCondition.VERY_GOOD
    assert listing.color == "blue"
    assert listing.delivery is True
