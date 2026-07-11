from app.domain.models import NormalizedListing


def risk_penalty(listing: NormalizedListing, median_price: float) -> tuple[float, str | None]:
    penalty = 0.0
    reasons: list[str] = []
    if median_price and float(listing.price) < median_price * 0.55:
        penalty += 15
        reasons.append("podejrzanie niska cena")
    if not listing.description or len(listing.description.strip()) < 40:
        penalty += 7
        reasons.append("bardzo krótki opis")
    if not listing.image_urls:
        penalty += 5
        reasons.append("brak zdjęć")
    text = f"{listing.title} {listing.description or ''}".casefold()
    if any(signal in text for signal in ("uszkodz", "nie działa", "na części", "blokada")):
        penalty += 15
        reasons.append("sygnał możliwej usterki")
    return min(30.0, penalty), reasons[0] if reasons else None
