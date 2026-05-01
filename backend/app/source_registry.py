from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class SourceConfig:
    """Configuración de una fuente de ofertas de empleo."""
    name: str
    kind: Literal["rss", "api", "html", "google"]
    endpoint: str
    country_hint: str = ""
    region_hint: str = ""
    requires_key: bool = False
    api_key_env: str = ""
    search_params: dict[str, str] = field(default_factory=dict)
    priority: int = 1  # 1 = alta, 5 = baja


# =============================================================================
# FUENTES GLOBALES - APIs y RSS de alcance mundial
# =============================================================================

GLOBAL_SOURCES: list[SourceConfig] = [
    # --- APIs de Empleo (más potentes, datos estructurados) ---
    SourceConfig(
        name="JSearch",
        kind="api",
        endpoint="https://jsearch.p.rapidapi.com/search",
        country_hint="Global",
        requires_key=True,
        api_key_env="RAPIDAPI_KEY",
        priority=1,
    ),
    SourceConfig(
        name="Adzuna",
        kind="api",
        endpoint="https://api.adzuna.com/v1/api/jobs",
        country_hint="Global",
        requires_key=True,
        api_key_env="ADZUNA_API_KEY",
        priority=1,
    ),
    SourceConfig(
        name="Arbeitnow",
        kind="api",
        endpoint="https://www.arbeitnow.com/api/job-board-api",
        country_hint="Global",
        requires_key=False,
        priority=2,
    ),
    SourceConfig(
        name="TheMuse",
        kind="api",
        endpoint="https://www.themuse.com/api/public/jobs",
        country_hint="Global",
        requires_key=False,
        priority=2,
    ),
    SourceConfig(
        name="Remotive",
        kind="api",
        endpoint="https://remotive.com/api/remote-jobs",
        country_hint="Global",
        requires_key=False,
        priority=2,
    ),
    
    # --- RSS Feeds Globales ---
    SourceConfig(
        name="RemoteOK",
        kind="rss",
        endpoint="https://remoteok.com/remote-jobs.rss",
        country_hint="Global",
        priority=2,
    ),
    SourceConfig(
        name="WeWorkRemotely",
        kind="rss",
        endpoint="https://weworkremotely.com/remote-jobs.rss",
        country_hint="Global",
        priority=2,
    ),
    SourceConfig(
        name="Jobicy",
        kind="rss",
        endpoint="https://jobicy.com/feed/newjobs",
        country_hint="Global",
        priority=3,
    ),
    SourceConfig(
        name="EuroRemoteJobs",
        kind="rss",
        endpoint="https://eurremotejobs.com/feed/",
        country_hint="Europa",
        priority=3,
    ),
]

# =============================================================================
# FUENTES LATINOAMERICANAS - Portales de empleo de la región
# =============================================================================

LATAM_SOURCES: list[SourceConfig] = [
    # --- Bolivia ---
    SourceConfig(
        name="Trabajo.bo",
        kind="html",
        endpoint="https://www.trabajo.bo/empleos",
        country_hint="Bolivia",
        priority=1,
    ),
    SourceConfig(
        name="CompuTrabajo Bolivia",
        kind="html",
        endpoint="https://www.computrabajo.com.bo/empleos",
        country_hint="Bolivia",
        priority=1,
    ),
    SourceConfig(
        name="Empleos Bolivia",
        kind="html",
        endpoint="https://empleos.bo/ofertas",
        country_hint="Bolivia",
        priority=1,
    ),
    SourceConfig(
        name="OpcionEmpleo Bolivia",
        kind="html",
        endpoint="https://www.opcionempleo.com.bo/",
        country_hint="Bolivia",
        priority=2,
    ),
    
    # --- Argentina ---
    SourceConfig(
        name="Bumeran Argentina",
        kind="html",
        endpoint="https://www.bumeran.com.ar/empleos.html",
        country_hint="Argentina",
        priority=2,
    ),
    SourceConfig(
        name="ZonaJobs Argentina",
        kind="html",
        endpoint="https://www.zonajobs.com.ar/ofertas-de-empleo",
        country_hint="Argentina",
        priority=2,
    ),
    SourceConfig(
        name="CompuTrabajo Argentina",
        kind="html",
        endpoint="https://www.computrabajo.com.ar/empleos",
        country_hint="Argentina",
        priority=2,
    ),
    
    # --- Chile ---
    SourceConfig(
        name="Trabajando Chile",
        kind="html",
        endpoint="https://www.trabajando.cl/empleos",
        country_hint="Chile",
        priority=2,
    ),
    SourceConfig(
        name="CompuTrabajo Chile",
        kind="html",
        endpoint="https://www.computrabajo.cl/empleos",
        country_hint="Chile",
        priority=2,
    ),
    
    # --- Perú ---
    SourceConfig(
        name="Bumeran Perú",
        kind="html",
        endpoint="https://www.bumeran.com.pe/empleos.html",
        country_hint="Perú",
        priority=2,
    ),
    SourceConfig(
        name="CompuTrabajo Perú",
        kind="html",
        endpoint="https://www.computrabajo.com.pe/empleos",
        country_hint="Perú",
        priority=2,
    ),
    
    # --- Colombia ---
    SourceConfig(
        name="CompuTrabajo Colombia",
        kind="html",
        endpoint="https://www.computrabajo.com.co/empleos",
        country_hint="Colombia",
        priority=2,
    ),
    SourceConfig(
        name="Magneto Empleos",
        kind="html",
        endpoint="https://www.magneto365.com/empleos",
        country_hint="Colombia",
        priority=2,
    ),
    
    # --- México ---
    SourceConfig(
        name="OCC Mundial",
        kind="html",
        endpoint="https://www.occ.com.mx/empleos/",
        country_hint="México",
        priority=2,
    ),
    SourceConfig(
        name="CompuTrabajo México",
        kind="html",
        endpoint="https://www.computrabajo.com.mx/empleos",
        country_hint="México",
        priority=2,
    ),
    SourceConfig(
        name="Indeed México",
        kind="html",
        endpoint="https://mx.indeed.com/empleos",
        country_hint="México",
        priority=2,
    ),
]

# =============================================================================
# FUENTES ESPAÑOLAS
# =============================================================================

SPAIN_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="InfoJobs",
        kind="html",
        endpoint="https://www.infojobs.net/jobsearch/search-results/list.xhtml",
        country_hint="España",
        priority=2,
    ),
    SourceConfig(
        name="Tecnoempleo",
        kind="rss",
        endpoint="https://www.tecnoempleo.com/rss/ofertas-empleo.xml",
        country_hint="España",
        priority=2,
    ),
    SourceConfig(
        name="LinkedIn España",
        kind="html",
        endpoint="https://es.linkedin.com/jobs",
        country_hint="España",
        priority=2,
    ),
]

# =============================================================================
# MOTOR DE BÚSQUEDA - Google Jobs (meta-buscador)
# =============================================================================

SEARCH_ENGINE_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="Google Jobs",
        kind="google",
        endpoint="https://www.google.com/search?q={query}+empleos+{location}&ibp=htl;jobs",
        country_hint="Global",
        priority=1,
    ),
    SourceConfig(
        name="SerpAPI Jobs",
        kind="api",
        endpoint="https://serpapi.com/search.json",
        country_hint="Global",
        requires_key=True,
        api_key_env="SERPAPI_KEY",
        search_params={"engine": "google_jobs"},
        priority=1,
    ),
]

# =============================================================================
# REGISTRO PRINCIPAL - Todas las fuentes combinadas
# =============================================================================

ALL_SOURCES: list[SourceConfig] = (
    GLOBAL_SOURCES + 
    LATAM_SOURCES + 
    SPAIN_SOURCES + 
    SEARCH_ENGINE_SOURCES
)

# Para compatibilidad con código existente
SOURCES = ALL_SOURCES


def get_sources_by_country(country: str) -> list[SourceConfig]:
    """Obtiene fuentes priorizadas para un país específico."""
    country_lower = country.lower().strip()
    
    prioritized: list[SourceConfig] = []
    others: list[SourceConfig] = []
    
    for source in ALL_SOURCES:
        hint = source.country_hint.lower()
        if country_lower in hint or hint == "global":
            prioritized.append(source)
        else:
            others.append(source)
    
    # Ordenar por prioridad (menor número = mayor prioridad)
    prioritized.sort(key=lambda s: s.priority)
    others.sort(key=lambda s: s.priority)
    
    return prioritized + others


def get_sources_by_region(region: str) -> list[SourceConfig]:
    """Obtiene fuentes para una región (Latinoamérica, Europa, etc.)."""
    region_lower = region.lower().strip()
    
    if "latin" in region_lower or "latam" in region_lower or "sudamerica" in region_lower:
        return sorted(LATAM_SOURCES + GLOBAL_SOURCES, key=lambda s: s.priority)
    elif "europ" in region_lower:
        return sorted(SPAIN_SOURCES + GLOBAL_SOURCES, key=lambda s: s.priority)
    else:
        return sorted(ALL_SOURCES, key=lambda s: s.priority)


# Mapeo de ciudades bolivianas a departamentos para mejor búsqueda
BOLIVIA_CITIES: dict[str, str] = {
    "la paz": "La Paz",
    "el alto": "La Paz",
    "santa cruz": "Santa Cruz",
    "cochabamba": "Cochabamba",
    "sucre": "Chuquisaca",
    "oruro": "Oruro",
    "potosi": "Potosí",
    "tarija": "Tarija",
    "trinidad": "Beni",
    "cobija": "Pando",
    "yacuiba": "Tarija",
    "villamontes": "Tarija",
    "bermejo": "Tarija",
    "montero": "Santa Cruz",
    "warnes": "Santa Cruz",
    "quillacollo": "Cochabamba",
    "sacaba": "Cochabamba",
    "riberalta": "Beni",
    "guayaramerin": "Beni",
}


def get_department_for_city(city: str) -> str | None:
    """Obtiene el departamento boliviano para una ciudad."""
    return BOLIVIA_CITIES.get(city.lower().strip())
