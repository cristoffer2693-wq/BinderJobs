from __future__ import annotations

from .models import JobOffer


def deduplicate(offers: list[JobOffer]) -> list[JobOffer]:
    """Elimina ofertas duplicadas por ID."""
    unique: dict[str, JobOffer] = {}
    for offer in offers:
        if offer.id not in unique:
            unique[offer.id] = offer
    return list(unique.values())


def score_offer(offer: JobOffer, query: str, country: str, city: str) -> float:
    """Calcula score de relevancia."""
    score = 0.0
    q = query.lower().strip()
    
    if q and (q in offer.title.lower() or q in offer.summary.lower()):
        score += 0.45
    if country and country.lower() in offer.country.lower():
        score += 0.30
    if city and city.lower() in offer.city.lower():
        score += 0.20
    if offer.modality.lower() == "remoto":
        score += 0.05
        
    return round(min(score, 0.99), 4)


def rank_offers(offers: list[JobOffer], query: str, country: str, city: str) -> list[JobOffer]:
    """Rankea ofertas por relevancia."""
    scored = []
    for offer in offers:
        s = score_offer(offer, query, country, city)
        scored.append(offer.model_copy(update={"score": s}))
    
    return sorted(scored, key=lambda x: x.score, reverse=True)
