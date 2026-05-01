from __future__ import annotations

from pydantic import BaseModel, HttpUrl, Field


class JobOffer(BaseModel):
    """Modelo de una oferta de trabajo."""
    id: str
    title: str
    company: str
    country: str
    city: str
    modality: str = "No especificado"
    salary: str | None = None
    summary: str
    source: str
    url: HttpUrl
    published_at: str
    score: float = 0.0
    
    # Campos adicionales para mejor ranking
    relevance_score: float = 0.0  # Qué tan relevante es para la búsqueda
    location_score: float = 0.0   # Qué tan cerca está del usuario
    preference_score: float = 0.0  # Qué tan bien coincide con preferencias


class SearchRequest(BaseModel):
    """Request para búsqueda avanzada."""
    query: str = Field(default="", description="Término de búsqueda")
    country: str = Field(default="", description="País del usuario")
    city: str = Field(default="", description="Ciudad del usuario")
    state: str = Field(default="", description="Departamento/Estado")
    modality: str = Field(default="", description="Modalidad preferida")
    salary_min: int = Field(default=0, ge=0, description="Salario mínimo")
    limit: int = Field(default=100, ge=1, le=500, description="Máximo resultados")
    
    # Preferencias de aprendizaje
    preferred_roles: list[str] = Field(default_factory=list)
    excluded_companies: list[str] = Field(default_factory=list)
    preferred_sources: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response de búsqueda con metadatos."""
    jobs: list[JobOffer]
    total_found: int
    sources_searched: int
    query: str
    location: str
    

class UserLocation(BaseModel):
    """Ubicación del usuario para búsqueda geográfica."""
    country: str = "Bolivia"
    state: str = ""  # Departamento
    city: str = ""
    latitude: float | None = None
    longitude: float | None = None
    radius_km: int = 50


class UserPreferences(BaseModel):
    """Preferencias del usuario para aprendizaje."""
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_modalities: list[str] = Field(default_factory=list)
    salary_min: int = 0
    salary_max: int | None = None
    excluded_companies: list[str] = Field(default_factory=list)
    saved_searches: list[str] = Field(default_factory=list)
    search_history: list[str] = Field(default_factory=list)
    clicked_offers: list[str] = Field(default_factory=list)  # IDs de ofertas clickeadas
    saved_offers: list[str] = Field(default_factory=list)    # IDs de ofertas guardadas


class BackgroundSearchConfig(BaseModel):
    """Configuración para búsqueda en segundo plano."""
    enabled: bool = True
    frequency_minutes: int = 30
    notify_on_new: bool = True
    search_query: str = ""
    min_score_to_notify: float = 0.5


class SearchQuery(BaseModel):
    """Query simple de búsqueda (compatibilidad)."""
    q: str = ""
    country: str = ""
    city: str = ""
