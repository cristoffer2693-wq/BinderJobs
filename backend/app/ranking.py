from __future__ import annotations

import re
from .models import JobOffer
from .source_registry import BOLIVIA_CITIES, get_department_for_city


def deduplicate(offers: list[JobOffer]) -> list[JobOffer]:
    """Elimina ofertas duplicadas por ID."""
    unique: dict[str, JobOffer] = {}
    for offer in offers:
        if offer.id not in unique:
            unique[offer.id] = offer
    return list(unique.values())


def normalize_text(text: str) -> str:
    """Normaliza texto para comparación."""
    text = text.lower().strip()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = re.sub(r"[ñ]", "n", text)
    return text


def calculate_location_score(
    offer: JobOffer,
    user_country: str,
    user_city: str,
    user_state: str = "",
    boost_local: bool = False,
) -> float:
    """
    Calcula score de ubicación.
    Prioriza: misma ciudad > mismo departamento > mismo país > global/remoto
    """
    score = 0.0
    
    offer_country = normalize_text(offer.country)
    offer_city = normalize_text(offer.city)
    user_country_norm = normalize_text(user_country)
    user_city_norm = normalize_text(user_city)
    user_state_norm = normalize_text(user_state)
    
    # Detectar departamento de la oferta si es Bolivia
    offer_state = ""
    if "bolivia" in offer_country:
        offer_state = get_department_for_city(offer_city) or ""
        offer_state = normalize_text(offer_state)
    
    # Misma ciudad = máxima prioridad
    if user_city_norm and user_city_norm in offer_city:
        score = 1.0 if boost_local else 0.5
    # Mismo departamento/estado
    elif user_state_norm and user_state_norm in offer_state:
        score = 0.8 if boost_local else 0.4
    # Mismo país
    elif user_country_norm and user_country_norm in offer_country:
        score = 0.6 if boost_local else 0.3
    # Trabajo remoto (disponible desde cualquier lugar)
    elif offer.modality.lower() == "remoto" or "remote" in offer_city.lower():
        score = 0.4 if boost_local else 0.25
    # Global sin restricción
    elif "global" in offer_country:
        score = 0.3 if boost_local else 0.2
    
    return score


def calculate_query_score(offer: JobOffer, query: str) -> float:
    """
    Calcula score de relevancia con el término de búsqueda.
    """
    if not query:
        return 0.0
    
    score = 0.0
    query_norm = normalize_text(query)
    query_words = query_norm.split()
    
    title_norm = normalize_text(offer.title)
    summary_norm = normalize_text(offer.summary)
    company_norm = normalize_text(offer.company)
    
    full_text = f"{title_norm} {summary_norm} {company_norm}"
    
    # Coincidencia exacta en título = máxima puntuación
    if query_norm in title_norm:
        score += 0.5
    
    # Coincidencia exacta en resumen
    if query_norm in summary_norm:
        score += 0.2
    
    # Coincidencia de palabras individuales
    words_matched = sum(1 for word in query_words if word in full_text)
    if query_words:
        word_ratio = words_matched / len(query_words)
        score += word_ratio * 0.25
    
    # Bonus si coincide con empresa
    if query_norm in company_norm:
        score += 0.1
    
    return min(score, 1.0)


def calculate_modality_score(offer: JobOffer, preferred_modality: str) -> float:
    """
    Calcula score basado en modalidad preferida.
    """
    if not preferred_modality:
        return 0.0
    
    offer_modality = normalize_text(offer.modality)
    preferred_norm = normalize_text(preferred_modality)
    
    if preferred_norm in offer_modality or offer_modality in preferred_norm:
        return 0.15
    
    # Remoto siempre tiene un pequeño bonus
    if "remoto" in offer_modality or "remote" in offer_modality:
        return 0.05
    
    return 0.0


def calculate_salary_score(offer: JobOffer, salary_min: int) -> float:
    """
    Calcula score basado en salario.
    """
    if salary_min <= 0 or not offer.salary:
        return 0.0
    
    # Extraer números del salario
    numbers = re.findall(r"[\d,]+", offer.salary.replace(",", ""))
    if not numbers:
        return 0.0
    
    try:
        salary_values = [int(n.replace(",", "")) for n in numbers]
        max_salary = max(salary_values)
        
        if max_salary >= salary_min:
            return 0.1
        elif max_salary >= salary_min * 0.8:
            return 0.05
    except ValueError:
        pass
    
    return 0.0


def score_offer(offer: JobOffer, query: str, country: str, city: str) -> float:
    """
    Función de scoring simple para compatibilidad.
    """
    score = 0.0
    
    query_score = calculate_query_score(offer, query)
    location_score = calculate_location_score(offer, country, city)
    
    score = query_score * 0.5 + location_score * 0.45
    
    # Pequeño bonus por trabajo remoto
    if offer.modality.lower() == "remoto":
        score += 0.05
    
    return round(min(score, 0.99), 4)


def score_offer_advanced(
    offer: JobOffer,
    query: str,
    country: str,
    city: str,
    state: str = "",
    preferred_modality: str = "",
    salary_min: int = 0,
    boost_local: bool = False,
) -> tuple[float, float, float, float]:
    """
    Scoring avanzado que devuelve scores individuales.
    Returns: (total_score, query_score, location_score, preference_score)
    """
    query_score = calculate_query_score(offer, query)
    location_score = calculate_location_score(offer, country, city, state, boost_local)
    modality_score = calculate_modality_score(offer, preferred_modality)
    salary_score = calculate_salary_score(offer, salary_min)
    
    preference_score = modality_score + salary_score
    
    # Pesos: ubicación es más importante si boost_local está activo
    if boost_local:
        total = (query_score * 0.3) + (location_score * 0.55) + (preference_score * 0.15)
    else:
        total = (query_score * 0.45) + (location_score * 0.40) + (preference_score * 0.15)
    
    return (round(min(total, 0.99), 4), query_score, location_score, preference_score)


def rank_offers(
    offers: list[JobOffer],
    query: str,
    country: str,
    city: str,
) -> list[JobOffer]:
    """
    Ranking simple para compatibilidad.
    """
    scored = []
    for offer in offers:
        score = score_offer(offer, query, country, city)
        scored.append(offer.model_copy(update={"score": score}))
    
    return sorted(scored, key=lambda item: item.score, reverse=True)


def rank_offers_with_preferences(
    offers: list[JobOffer],
    query: str,
    country: str,
    city: str,
    state: str = "",
    preferred_modality: str = "",
    salary_min: int = 0,
    boost_local: bool = False,
) -> list[JobOffer]:
    """
    Ranking avanzado con todas las preferencias del usuario.
    Ideal para búsqueda personalizada.
    """
    scored = []
    
    for offer in offers:
        total, q_score, loc_score, pref_score = score_offer_advanced(
            offer=offer,
            query=query,
            country=country,
            city=city,
            state=state,
            preferred_modality=preferred_modality,
            salary_min=salary_min,
            boost_local=boost_local,
        )
        
        updated = offer.model_copy(update={
            "score": total,
            "relevance_score": q_score,
            "location_score": loc_score,
            "preference_score": pref_score,
        })
        scored.append(updated)
    
    # Ordenar por score total descendente
    scored.sort(key=lambda item: item.score, reverse=True)
    
    return scored


def filter_by_location(
    offers: list[JobOffer],
    country: str,
    city: str = "",
    include_remote: bool = True,
) -> list[JobOffer]:
    """
    Filtra ofertas por ubicación estricta.
    """
    country_norm = normalize_text(country)
    city_norm = normalize_text(city)
    
    filtered = []
    for offer in offers:
        offer_country = normalize_text(offer.country)
        offer_city = normalize_text(offer.city)
        
        # Coincide con país
        country_match = country_norm in offer_country or offer_country in country_norm
        
        # Coincide con ciudad (si se especifica)
        city_match = not city_norm or city_norm in offer_city
        
        # Es remoto
        is_remote = offer.modality.lower() == "remoto" or "remote" in offer_city
        
        if (country_match and city_match) or (include_remote and is_remote):
            filtered.append(offer)
    
    return filtered
