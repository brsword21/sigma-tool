from decimal import Decimal

from app.domain.models import ListingCondition, NormalizedListing, Requirements
from app.product_matching import matches_product_title
from app.ranking.engine import matches_exact_product, rank_listings


def listing(
    external_id: str, price: str, condition: ListingCondition, description: str, images: int = 2
) -> NormalizedListing:
    return NormalizedListing(
        source="fixture",
        external_id=external_id,
        url=f"https://example.com/{external_id}",
        title="Sony WH-1000XM4 blue ANC",
        price=Decimal(price),
        condition=condition,
        color="blue",
        delivery=True,
        description=description,
        attributes={"variant": "wireless", "feature": "ANC"},
        image_urls=[f"https://example.com/{external_id}-{index}.jpg" for index in range(images)],
    )


def test_three_listings_get_stable_order_and_exact_breakdown() -> None:
    description = (
        "Kompletne sprawne słuchawki z etui, ładowarką i możliwością wysyłki, bez widocznych wad."
    )
    results = rank_listings(
        [
            listing("cheap-risk", "150", ListingCondition.UNKNOWN, "Krótki opis", 0),
            listing("best", "420", ListingCondition.VERY_GOOD, description, 4),
            listing("expensive", "500", ListingCondition.GOOD, description),
        ],
        Requirements(
            budget_max=Decimal("500"),
            required_features=["ANC"],
            preferred_colors=["blue"],
            delivery_required=True,
        ),
    )
    assert [item.listing.external_id for item in results] == ["best", "expensive", "cheap-risk"]
    assert results[0].score == results[0].score_breakdown.total
    assert len(results[0].strengths) == 3
    assert results[-1].score_breakdown.risk_penalty > 0


def test_hard_budget_filter_runs_before_scoring() -> None:
    results = rank_listings(
        [listing("over", "501", ListingCondition.NEW, "x" * 100)],
        Requirements(budget_max=Decimal("500")),
    )
    assert results == []


def test_exact_generation_is_verified_before_scoring() -> None:
    first_generation = listing(
        "gen-1", "400", ListingCondition.VERY_GOOD, "Apple AirPods Pro 1. generacji"
    ).model_copy(update={"title": "Apple AirPods Pro 1. generacji"})
    second_generation = listing(
        "gen-2", "450", ListingCondition.VERY_GOOD, "Apple AirPods Pro 2. generacji"
    ).model_copy(update={"title": "Apple AirPods Pro 2. generacji"})
    product = {"model": "AirPods Pro 2 gen", "specifications": {}}

    assert matches_exact_product(first_generation, product) is False
    assert matches_exact_product(second_generation, product) is True


def test_exact_product_rejects_accessories_and_description_only_mentions() -> None:
    product = {"brand": "Apple", "model": "iPhone 15", "specifications": {}}
    phone = listing(
        "iphone", "2000", ListingCondition.VERY_GOOD, "Sprawny telefon, bateria 91%."
    ).model_copy(update={"title": "Apple iPhone 15 128 GB czarny"})
    case = listing(
        "case", "50", ListingCondition.NEW, "Etui kompatybilne z Apple iPhone 15."
    ).model_copy(update={"title": "Etui ochronne do Apple iPhone 15"})
    unrelated = listing(
        "unrelated", "1400", ListingCondition.VERY_GOOD, "Sprzedaję, bo kupiłem iPhone 15."
    ).model_copy(update={"title": "Samsung Galaxy A54"})

    assert matches_exact_product(phone, product) is True
    assert matches_exact_product(case, product) is False
    assert matches_exact_product(unrelated, product) is False


def test_exact_product_rejects_an_olx_search_page_from_an_old_cache() -> None:
    product = {"brand": "Sony", "model": "WF-1000XM4", "specifications": {}}
    search_page = listing(
        "olx-search", "199", ListingCondition.GOOD, "Sony WF-1000XM4 używane."
    ).model_copy(
        update={
            "source": "olx_firecrawl",
            "url": "https://www.olx.pl/elektronika/q-sony-wf-1000xm4/",
            "title": "Sony WF-1000XM4 - wyniki OLX",
        }
    )

    assert matches_exact_product(search_page, product) is False


def test_product_title_match_is_canonical_and_rejects_noise_and_accessories() -> None:
    assert matches_product_title("Samsung Galaxy S25 256 GB", "Samsung Galaxy S25") is True
    assert matches_product_title("Sony WF-1000XM4 używane", "Sony WF-1000XM4") is True
    assert matches_product_title("iPhone 17 Air 256 GB", "Samsung Galaxy S25") is False
    assert matches_product_title("Etui do Samsung Galaxy S25", "Samsung Galaxy S25") is False


def test_brief_parameters_lift_matching_listing_and_explanation() -> None:
    generic = (
        "Kompletne sprawne słuchawki z etui, ładowarką i możliwością wysyłki, bez widocznych wad."
    )
    with_codec = generic + " Obsługuje kodek LDAC i mają świetny mikrofon."
    brief = {
        "key_parameters": {"kodek": "LDAC", "mikrofon": "tak"},
        "known_risks": ["sprawdź żywotność baterii"],
    }
    # Generic offer is a touch cheaper, so it wins on price alone until the brief weighs in.
    listings = [
        listing("generic", "380", ListingCondition.VERY_GOOD, generic, 4),
        listing("device-fit", "420", ListingCondition.VERY_GOOD, with_codec, 4),
    ]
    without_brief = rank_listings(listings, Requirements(budget_max=Decimal("500")))
    with_brief = rank_listings(listings, Requirements(budget_max=Decimal("500")), brief)

    # Same price/condition: the brief is the tie-breaker that promotes the device-fit offer.
    assert without_brief[0].listing.external_id == "generic"
    assert with_brief[0].listing.external_id == "device-fit"
    top, runner_up = with_brief[0], with_brief[1]
    assert top.explanation is not None and "ldac" in top.explanation.casefold()
    assert top.product_match_score > runner_up.product_match_score


def test_ranking_is_unchanged_when_brief_has_no_parameters() -> None:
    listings = [listing("a", "400", ListingCondition.VERY_GOOD, "x" * 100, 4)]
    baseline = rank_listings(listings, Requirements(budget_max=Decimal("500")))
    with_empty_brief = rank_listings(
        listings, Requirements(budget_max=Decimal("500")), {"summary": "brak parametrów"}
    )
    assert baseline[0].score == with_empty_brief[0].score
    assert with_empty_brief[0].explanation is None
