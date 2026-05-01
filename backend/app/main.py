from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Any

from .models import JobOffer
from .ranking import deduplicate, rank_offers

app = FastAPI(
    title="BinderJobs Search Engine API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "BinderJobs API", "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0", "engine": "BinderJobs Search"}


@app.get("/jobs/search", response_model=list[JobOffer])
def search_jobs(
    q: str = Query(default=""),
    country: str = Query(default=""),
    city: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[JobOffer]:
    """Busca ofertas de empleo."""
    from .crawler import crawl_all_sources
    
    try:
        offers = crawl_all_sources()
    except Exception:
        offers = []
    
    if not offers:
        offers = get_sample_jobs()
    
    deduped = deduplicate(offers)
    ranked = rank_offers(deduped, q, country, city)
    
    return ranked[:limit]


@app.get("/sources")
def list_sources() -> dict[str, Any]:
    return {
        "total_sources": 5,
        "sources": [
            {"name": "RemoteOK", "type": "rss"},
            {"name": "Remotive", "type": "api"},
            {"name": "Arbeitnow", "type": "api"},
        ],
    }


def get_sample_jobs() -> list[JobOffer]:
    """Ofertas de ejemplo cuando no hay conexión."""
    return [
        JobOffer(
            id="sample-1",
            title="Desarrollador Android",
            company="TechBolivia",
            country="Bolivia",
            city="Tarija",
            modality="Presencial",
            salary="Bs. 5,000 - 8,000",
            summary="Desarrollo de aplicaciones móviles con Kotlin.",
            source="BinderJobs",
            url="https://www.computrabajo.com.bo/",
            published_at="Reciente",
        ),
        JobOffer(
            id="sample-2",
            title="Programador Web Full Stack",
            company="RemoteLATAM",
            country="Bolivia",
            city="Remoto",
            modality="Remoto",
            salary="USD 800 - 1,500",
            summary="Desarrollo web con React y Node.js.",
            source="BinderJobs",
            url="https://remoteok.com/",
            published_at="Reciente",
        ),
        JobOffer(
            id="sample-3",
            title="Analista de Datos",
            company="DataCorp",
            country="Bolivia",
            city="La Paz",
            modality="Híbrido",
            salary="Bs. 6,000+",
            summary="Análisis de datos con Python y SQL.",
            source="BinderJobs",
            url="https://www.trabajo.bo/",
            published_at="Reciente",
        ),
    ]
