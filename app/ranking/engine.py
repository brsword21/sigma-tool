from statistics import median

from app.domain.models import (
    ListingCondition,
    NormalizedListing,
    RankedListing,
    Requirements,
    ScoreBreakdown,
)
from app.ranking.risk import risk_penalty

_CONDITION_POINTS = {
    ListingCondition.NEW: 20,
    ListingCondition.LIKE_NEW: 19,
    ListingCondition.VERY_GOOD: 17,
    ListingCondition.GOOD: 14,
    ListingCondition.FAIR: 7,
    ListingCondition.UNKNOWN: 9,
}


def rank_listings(
    listings: list[NormalizedListing], requirements: Requirements
) -> list[RankedListing]:
    filtered = [listing for listing in listings if _passes_hard_filters(listing, requirements)]
    if not filtered:
        return []
    median_price = float(median(float(item.price) for item in filtered))
    ranked = [_score(item, requirements, median_price) for item in filtered]
    return sorted(
        ranked, key=lambda item: (-item.score, float(item.listing.price), item.listing.external_id)
    )


def _passes_hard_filters(listing: NormalizedListing, requirements: Requirements) -> bool:
    if requirements.budget_max is not None and listing.price > requirements.budget_max:
        return False
    if requirements.delivery_required is True and listing.delivery is not True:
        return False
    haystack = f"{listing.title} {listing.description or ''} {listing.attributes}".casefold()
    return all(
        term.casefold() in haystack
        for term in requirements.required_variants + requirements.required_features
    )


def _score(
    listing: NormalizedListing, requirements: Requirements, median_price: float
) -> RankedListing:
    ratio = float(listing.price) / median_price if median_price else 1
    price = max(0.0, min(30.0, 15 + (1 - ratio) * 30))
    haystack = f"{listing.title} {listing.description or ''} {listing.attributes}".casefold()
    required = requirements.required_variants + requirements.required_features
    req_score = (
        25.0
        if not required
        else 25 * sum(term.casefold() in haystack for term in required) / len(required)
    )
    completeness = min(
        10.0,
        (4 if listing.description and len(listing.description) >= 80 else 2)
        + min(4, len(listing.image_urls))
        + (2 if len(listing.attributes) >= 2 else 0),
    )
    logistics = (
        10.0
        if requirements.delivery_required and listing.delivery
        else 7.0
        if listing.delivery
        else 5.0
    )
    preferences = requirements.preferred_features + requirements.preferred_colors
    preference_score = (
        5.0
        if not preferences
        else 5 * sum(term.casefold() in haystack for term in preferences) / len(preferences)
    )
    penalty, risk = risk_penalty(listing, median_price)
    breakdown = ScoreBreakdown(
        price=round(price, 2),
        requirements=round(req_score, 2),
        condition=_CONDITION_POINTS[listing.condition],
        completeness=completeness,
        logistics=logistics,
        preferences=round(preference_score, 2),
        risk_penalty=penalty,
    )
    strengths = sorted(
        (
            (breakdown.price / 30, "korzystna cena"),
            (breakdown.requirements / 25, "zgodność z wymaganiami"),
            (breakdown.condition / 20, "dobry deklarowany stan"),
            (breakdown.completeness / 10, "kompletne ogłoszenie"),
            (breakdown.logistics / 10, "wygodna dostawa lub lokalizacja"),
            (breakdown.preferences / 5, "zgodność z preferencjami"),
        ),
        reverse=True,
    )
    return RankedListing(
        listing=listing,
        score=breakdown.total,
        score_breakdown=breakdown,
        strengths=[text for _, text in strengths[:3]],
        risk_or_tradeoff=risk,
    )
