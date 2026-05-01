from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .crawler import search_all_sources, crawl_all_sources
from .models import JobOffer, SearchRequest, SearchResponse, UserLocation
from .ranking import deduplicate, rank_offers, rank_offers_with_preferences
from .source_registry import ALL_SOURCES, get_sources_by_country, BOLIVIA_CITIES

app = FastAPI(
    title="BinderJobs Search Engine API",
    description="Motor de búsqueda de empleo - Busca en múltiples fuentes de internet",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0", "engine": "BinderJobs Search"}


@app.get("/jobs/search", response_model=list[JobOffer])
async def search_jobs(
    q: str = Query(default="", description="Término de búsqueda (puesto, habilidad, empresa)"),
    country: str = Query(default="", description="País del usuario"),
    city: str = Query(default="", description="Ciudad del usuario"),
    state: str = Query(default="", description="Departamento/Estado"),
    modality: str = Query(default="", description="Modalidad: Remoto, Presencial, Híbrido"),
    salary_min: int = Query(default=0, description="Salario mínimo deseado"),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de resultados"),
) -> list[JobOffer]:
    """
    Endpoint principal de búsqueda.
    Busca en todas las fuentes disponibles y rankea por relevancia + ubicación.
    """
    offers = await search_all_sources(
        query=q,
        country=country,
        city=city,
    )
    
    deduped = deduplicate(offers)
    
    ranked = rank_offers_with_preferences(
        offers=deduped,
        query=q,
        country=country,
        city=city,
        state=state,
        preferred_modality=modality,
        salary_min=salary_min,
    )
    
    return ranked[:limit]


@app.post("/jobs/search", response_model=SearchResponse)
async def search_jobs_advanced(request: SearchRequest) -> SearchResponse:
    """
    Búsqueda avanzada con todas las preferencias del usuario.
    Ideal para la app Android con configuración completa.
    """
    offers = await search_all_sources(
        query=request.query,
        country=request.country,
        city=request.city,
    )
    
    deduped = deduplicate(offers)
    
    ranked = rank_offers_with_preferences(
        offers=deduped,
        query=request.query,
        country=request.country,
        city=request.city,
        state=request.state,
        preferred_modality=request.modality,
        salary_min=request.salary_min,
    )
    
    limited = ranked[:request.limit]
    
    return SearchResponse(
        jobs=limited,
        total_found=len(deduped),
        sources_searched=len(get_sources_by_country(request.country) if request.country else ALL_SOURCES),
        query=request.query,
        location=f"{request.city}, {request.country}".strip(", "),
    )


@app.get("/jobs/nearby", response_model=list[JobOffer])
async def search_nearby_jobs(
    city: str = Query(..., description="Ciudad del usuario"),
    country: str = Query(default="Bolivia", description="País del usuario"),
    radius_km: int = Query(default=50, description="Radio de búsqueda en km"),
    q: str = Query(default="", description="Filtro opcional por término"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[JobOffer]:
    """
    Busca empleos cercanos a la ubicación del usuario.
    Prioriza ofertas de la misma ciudad y departamento.
    """
    state = ""
    city_lower = city.lower().strip()
    if city_lower in BOLIVIA_CITIES:
        state = BOLIVIA_CITIES[city_lower]
    
    offers = await search_all_sources(
        query=q,
        country=country,
        city=city,
    )
    
    deduped = deduplicate(offers)
    
    ranked = rank_offers_with_preferences(
        offers=deduped,
        query=q,
        country=country,
        city=city,
        state=state,
        preferred_modality="",
        salary_min=0,
        boost_local=True,
    )
    
    return ranked[:limit]


@app.get("/sources")
def list_sources() -> dict[str, any]:
    """Lista todas las fuentes de datos disponibles."""
    sources_info = []
    for source in ALL_SOURCES:
        sources_info.append({
            "name": source.name,
            "type": source.kind,
            "country": source.country_hint,
            "requires_api_key": source.requires_key,
            "priority": source.priority,
        })
    
    return {
        "total_sources": len(ALL_SOURCES),
        "sources": sources_info,
    }


@app.get("/sources/by-country/{country}")
def list_sources_by_country(country: str) -> dict[str, any]:
    """Lista fuentes priorizadas para un país específico."""
    sources = get_sources_by_country(country)
    
    return {
        "country": country,
        "total_sources": len(sources),
        "sources": [
            {
                "name": s.name,
                "type": s.kind,
                "priority": s.priority,
            }
            for s in sources[:20]
        ],
    }


@app.get("/location/bolivia/cities")
def get_bolivia_cities() -> dict[str, list[str]]:
    """Devuelve las ciudades bolivianas organizadas por departamento."""
    cities_by_department: dict[str, list[str]] = {}
    
    for city, department in BOLIVIA_CITIES.items():
        if department not in cities_by_department:
            cities_by_department[department] = []
        cities_by_department[department].append(city.title())
    
    return cities_by_department


@app.post("/background/search", response_model=SearchResponse)
async def background_search(request: SearchRequest) -> SearchResponse:
    """
    Endpoint para búsqueda en segundo plano.
    Usado por el WorkManager de Android para notificaciones.
    """
    offers = await search_all_sources(
        query=request.query,
        country=request.country,
        city=request.city,
        max_sources=10,
    )
    
    deduped = deduplicate(offers)
    ranked = rank_offers_with_preferences(
        offers=deduped,
        query=request.query,
        country=request.country,
        city=request.city,
        state=request.state,
        preferred_modality=request.modality,
        salary_min=request.salary_min,
    )
    
    limited = ranked[:request.limit]
    
    return SearchResponse(
        jobs=limited,
        total_found=len(deduped),
        sources_searched=10,
        query=request.query,
        location=f"{request.city}, {request.country}".strip(", "),
    )
