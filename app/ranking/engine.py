import re
from statistics import median
from typing import Any

from app.domain.models import (
    ListingCondition,
    NormalizedListing,
    RankedListing,
    Requirements,
    ScoreBreakdown,
)
from app.product_matching import (
    canonical_product_text,
    is_direct_olx_listing_url,
    matches_product_title,
)
from app.ranking.risk import risk_penalty

_BATTERY_PATTERN = re.compile(
    r"(?:bat\w*|kondycj\w*|zdrowi\w*|health)\W{0,4}(\d{2,3})\s*%"
    r"|(\d{2,3})\s*%\s*(?:bat\w*|kondycj\w*|zdrowi\w*|health)",
    re.IGNORECASE | re.UNICODE,
)
_CAPACITY_PATTERN = re.compile(r"(\d{2,4})\s*(gb|tb)\b", re.IGNORECASE)


def extract_battery_health(text: str) -> int | None:
    match = _BATTERY_PATTERN.search(text)
    if not match:
        return None
    value = int(match.group(1) or match.group(2))
    return value if 40 <= value <= 100 else None


_CONDITION_POINTS = {
    ListingCondition.NEW: 20,
    ListingCondition.LIKE_NEW: 19,
    ListingCondition.VERY_GOOD: 17,
    ListingCondition.GOOD: 14,
    ListingCondition.FAIR: 7,
    ListingCondition.UNKNOWN: 9,
}


def rank_listings(
    listings: list[NormalizedListing],
    requirements: Requirements,
    brief: dict[str, Any] | None = None,
) -> list[RankedListing]:
    filtered = [listing for listing in listings if _passes_hard_filters(listing, requirements)]
    if not filtered:
        return []
    brief_terms = _brief_terms(brief)
    brief_risks = _brief_risks(brief)
    median_price = float(median(float(item.price) for item in filtered))
    ranked = [
        _score(item, requirements, median_price, brief_terms, brief_risks) for item in filtered
    ]
    return sorted(
        ranked, key=lambda item: (-item.score, float(item.listing.price), item.listing.external_id)
    )


def matches_exact_product(listing: NormalizedListing, product: dict[str, Any]) -> bool:
    if listing.source == "olx_firecrawl" and not is_direct_olx_listing_url(str(listing.url)):
        return False
    specifications = product.get("specifications") or {}
    expected = str(specifications.get("exact_variant") or product.get("model") or "").strip()
    if not expected:
        return False
    canonical_expected = canonical_product_text(expected)
    canonical_declared_variant = canonical_product_text(listing.exact_variant or "")
    return (
        matches_product_title(listing.title, expected)
        or canonical_expected in canonical_declared_variant
    )


def _brief_terms(brief: dict[str, Any] | None) -> list[str]:
    if not brief:
        return []
    parameters = brief.get("key_parameters")
    if not isinstance(parameters, dict):
        return []
    terms: list[str] = []
    for key, value in parameters.items():
        terms.append(str(key))
        if isinstance(value, (str, int, float)):
            terms.append(str(value))
        elif isinstance(value, list):
            terms.extend(str(item) for item in value if isinstance(item, (str, int, float)))
    seen: dict[str, None] = {}
    for term in terms:
        folded = term.strip().casefold()
        if len(folded) >= 3:
            seen.setdefault(folded, None)
    return list(seen)


def _brief_risks(brief: dict[str, Any] | None) -> list[str]:
    if not brief:
        return []
    risks = brief.get("known_risks")
    return [str(risk) for risk in risks if isinstance(risk, str)] if isinstance(risks, list) else []


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
    listing: NormalizedListing,
    requirements: Requirements,
    median_price: float,
    brief_terms: list[str] | None = None,
    brief_risks: list[str] | None = None,
) -> RankedListing:
    brief_terms = brief_terms or []
    brief_risks = brief_risks or []
    ratio = float(listing.price) / median_price if median_price else 1
    price = max(0.0, min(30.0, 15 + (1 - ratio) * 30))
    haystack = f"{listing.title} {listing.description or ''} {listing.attributes}".casefold()
    required = requirements.required_variants + requirements.required_features
    user_fraction = (
        1.0
        if not required
        else sum(term.casefold() in haystack for term in required) / len(required)
    )
    matched_brief = [term for term in brief_terms if term in haystack]
    if brief_terms:
        brief_fraction = len(matched_brief) / len(brief_terms)
        req_score = 25 * (0.7 * user_fraction + 0.3 * brief_fraction)
    else:
        req_score = 25 * user_fraction
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
    seller_rating = listing.seller_signals.get("seller_rating")
    try:
        seller_trust = max(0.0, min(100.0, float(seller_rating) * 20))
    except (TypeError, ValueError):
        seller_trust = 40.0
    product_match = round((req_score / 25 * 80) + (preference_score / 5 * 20), 2)
    offer_quality = round(
        (price / 30 * 35)
        + (_CONDITION_POINTS[listing.condition] / 20 * 30)
        + (completeness / 10 * 20)
        + (logistics / 10 * 15),
        2,
    )
    strength_texts = [text for _, text in strengths[:3]]
    explanation = _build_explanation(listing, median_price, matched_brief, brief_risks, risk)
    return RankedListing(
        listing=listing,
        score=breakdown.total,
        score_breakdown=breakdown,
        strengths=strength_texts,
        risk_or_tradeoff=risk,
        explanation=explanation,
        product_match_score=product_match,
        offer_quality_score=offer_quality,
        seller_trust_score=seller_trust,
        confidence=listing.confidence,
        data_gaps=listing.data_gaps,
    )


def _build_explanation(
    listing: NormalizedListing,
    median_price: float,
    matched_brief: list[str],
    brief_risks: list[str],
    risk: str | None,
) -> str | None:
    # Fallback used when the LLM explanation is unavailable: only facts that
    # come from this specific listing, never generic scoring labels.
    text = f"{listing.title} {listing.description or ''}"
    parts: list[str] = []
    ratio = float(listing.price) / median_price if median_price else 1.0
    if ratio <= 0.93:
        parts.append(f"cena {round((1 - ratio) * 100)}% poniżej mediany porównywanych ofert")
    elif ratio >= 1.07:
        parts.append(f"cena {round((ratio - 1) * 100)}% powyżej mediany porównywanych ofert")
    battery = extract_battery_health(text)
    if battery is not None:
        parts.append(f"sprzedawca deklaruje kondycję baterii {battery}%")
    if listing.warranty:
        parts.append(f"gwarancja: {listing.warranty}")
    title_folded = listing.title.casefold()
    confirmed = [term for term in matched_brief if term not in title_folded]
    if confirmed:
        parts.append("potwierdzone w treści ogłoszenia: " + ", ".join(confirmed[:3]))
    if risk:
        parts.append(f"uwaga: {risk}")
    elif brief_risks:
        parts.append(f"sprawdź przed zakupem: {brief_risks[0]}")
    return "; ".join(parts[:4]) if parts else None
