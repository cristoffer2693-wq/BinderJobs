from __future__ import annotations

import asyncio
import hashlib
import os
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus, urljoin

import feedparser
import httpx
from bs4 import BeautifulSoup

from .models import JobOffer
from .source_registry import (
    ALL_SOURCES,
    SourceConfig,
    get_sources_by_country,
    get_department_for_city,
)


def _canonical_id(title: str, company: str, city: str, url: str) -> str:
    """Genera un ID único para evitar duplicados."""
    raw = f"{title.strip().lower()}|{company.strip().lower()}|{city.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _extract_company(source_name: str, title: str) -> str:
    """Extrae el nombre de la empresa del título si es posible."""
    patterns = [
        r" at (.+)$",
        r" en (.+)$",
        r" - (.+)$",
        r" \| (.+)$",
        r" @ (.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return source_name


def _clean_text(text: str, max_length: int = 300) -> str:
    """Limpia y trunca texto HTML."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(" ", strip=True)
    clean = re.sub(r"\s+", " ", clean)
    return clean[:max_length] if len(clean) > max_length else clean


def _extract_salary(text: str) -> str | None:
    """Intenta extraer información de salario del texto."""
    patterns = [
        r"\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:USD|BOB|ARS|MXN|CLP|PEN|COP))?",
        r"(?:USD|BOB|ARS|MXN|CLP|PEN|COP)\s*[\d,]+(?:\s*-\s*[\d,]+)?",
        r"Bs\.?\s*[\d,]+(?:\s*-\s*[\d,]+)?",
        r"[\d,]+\s*(?:USD|BOB|ARS|MXN|CLP|PEN|COP)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _detect_modality(text: str) -> str:
    """Detecta la modalidad de trabajo."""
    text_lower = text.lower()
    if any(word in text_lower for word in ["remoto", "remote", "trabajo desde casa", "home office", "teletrabajo"]):
        return "Remoto"
    if any(word in text_lower for word in ["híbrido", "hybrid", "mixto"]):
        return "Híbrido"
    if any(word in text_lower for word in ["presencial", "on-site", "onsite", "oficina"]):
        return "Presencial"
    return "No especificado"


def _detect_city_country(text: str, source_hint: str = "") -> tuple[str, str]:
    """Intenta detectar ciudad y país del texto."""
    text_lower = text.lower()
    
    bolivia_cities = {
        "tarija": ("Tarija", "Bolivia"),
        "la paz": ("La Paz", "Bolivia"),
        "santa cruz": ("Santa Cruz", "Bolivia"),
        "cochabamba": ("Cochabamba", "Bolivia"),
        "sucre": ("Sucre", "Bolivia"),
        "oruro": ("Oruro", "Bolivia"),
        "potosí": ("Potosí", "Bolivia"),
        "potosi": ("Potosí", "Bolivia"),
        "el alto": ("El Alto", "Bolivia"),
    }
    
    for city_key, (city, country) in bolivia_cities.items():
        if city_key in text_lower:
            return city, country
    
    country_keywords = {
        "bolivia": "Bolivia",
        "argentina": "Argentina",
        "chile": "Chile",
        "perú": "Perú",
        "peru": "Perú",
        "colombia": "Colombia",
        "méxico": "México",
        "mexico": "México",
        "españa": "España",
        "spain": "España",
        "united states": "Estados Unidos",
        "usa": "Estados Unidos",
    }
    
    for keyword, country in country_keywords.items():
        if keyword in text_lower:
            return "", country
    
    if source_hint:
        return "", source_hint
    
    return "", "Global"


# =============================================================================
# CRAWLERS POR TIPO DE FUENTE
# =============================================================================

async def crawl_rss(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """Crawlea feeds RSS."""
    offers: list[JobOffer] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(source.endpoint)
            response.raise_for_status()
            
        parsed = feedparser.parse(response.text)
        query_lower = query.lower() if query else ""
        location_lower = location.lower() if location else ""
        
        for entry in parsed.entries[:100]:
            title = entry.get("title", "Vacante")
            link = entry.get("link", "")
            if not link:
                continue
                
            summary = _clean_text(entry.get("summary", entry.get("description", "")))
            full_text = f"{title} {summary}"
            
            if query_lower and query_lower not in full_text.lower():
                continue
            
            city, country = _detect_city_country(full_text, source.country_hint)
            if location_lower and location_lower not in f"{city} {country}".lower():
                if source.country_hint.lower() != "global":
                    continue
            
            company = _extract_company(source.name, title)
            modality = _detect_modality(full_text)
            salary = _extract_salary(full_text)
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, city, link),
                    title=title,
                    company=company,
                    country=country if country else source.country_hint,
                    city=city if city else ("Remoto" if modality == "Remoto" else ""),
                    modality=modality,
                    salary=salary,
                    summary=summary or "Sin descripción",
                    source=source.name,
                    url=link,
                    published_at=_now_label(),
                )
            )
    except Exception as e:
        print(f"Error crawling RSS {source.name}: {e}")
    
    return offers


async def crawl_api_arbeitnow(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """Crawlea la API de Arbeitnow (gratuita, sin API key)."""
    offers: list[JobOffer] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(source.endpoint)
            response.raise_for_status()
            data = response.json()
            
        jobs = data.get("data", [])
        query_lower = query.lower() if query else ""
        location_lower = location.lower() if location else ""
        
        for job in jobs[:100]:
            title = job.get("title", "Vacante")
            company = job.get("company_name", "Empresa")
            job_location = job.get("location", "")
            description = _clean_text(job.get("description", ""))
            url = job.get("url", "")
            remote = job.get("remote", False)
            
            if not url:
                continue
            
            full_text = f"{title} {description} {job_location}"
            
            if query_lower and query_lower not in full_text.lower():
                continue
            
            city, country = _detect_city_country(job_location)
            if not country:
                country = "Global" if remote else source.country_hint
            
            if location_lower and location_lower not in f"{city} {country} {job_location}".lower():
                if not remote:
                    continue
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, city, url),
                    title=title,
                    company=company,
                    country=country,
                    city=city if city else job_location,
                    modality="Remoto" if remote else "Presencial",
                    salary=None,
                    summary=description or "Sin descripción",
                    source=source.name,
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception as e:
        print(f"Error crawling Arbeitnow: {e}")
    
    return offers


async def crawl_api_remotive(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """Crawlea la API de Remotive (gratuita)."""
    offers: list[JobOffer] = []
    try:
        params = {}
        if query:
            params["search"] = query
            
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(source.endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
        jobs = data.get("jobs", [])
        location_lower = location.lower() if location else ""
        
        for job in jobs[:100]:
            title = job.get("title", "Vacante")
            company = job.get("company_name", "Empresa")
            candidate_location = job.get("candidate_required_location", "Worldwide")
            description = _clean_text(job.get("description", ""))
            url = job.get("url", "")
            salary = job.get("salary", "")
            
            if not url:
                continue
            
            city, country = _detect_city_country(candidate_location)
            
            if location_lower:
                if location_lower not in candidate_location.lower() and "worldwide" not in candidate_location.lower():
                    continue
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, "", url),
                    title=title,
                    company=company,
                    country=country if country else "Global",
                    city=city if city else "Remoto",
                    modality="Remoto",
                    salary=salary if salary else None,
                    summary=description or "Sin descripción",
                    source=source.name,
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception as e:
        print(f"Error crawling Remotive: {e}")
    
    return offers


async def crawl_api_themuse(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """Crawlea la API de The Muse (gratuita)."""
    offers: list[JobOffer] = []
    try:
        params = {"page": 1}
        if query:
            params["category"] = query
            
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(source.endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
        jobs = data.get("results", [])
        location_lower = location.lower() if location else ""
        
        for job in jobs[:100]:
            title = job.get("name", "Vacante")
            company_data = job.get("company", {})
            company = company_data.get("name", "Empresa") if isinstance(company_data, dict) else "Empresa"
            locations = job.get("locations", [])
            location_str = ", ".join([loc.get("name", "") for loc in locations]) if locations else "No especificado"
            description = _clean_text(job.get("contents", ""))
            
            refs = job.get("refs", {})
            url = refs.get("landing_page", "") if isinstance(refs, dict) else ""
            
            if not url:
                continue
            
            city, country = _detect_city_country(location_str)
            
            if location_lower and location_lower not in location_str.lower():
                continue
            
            modality = _detect_modality(f"{title} {location_str}")
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, city, url),
                    title=title,
                    company=company,
                    country=country if country else "Estados Unidos",
                    city=city if city else location_str[:50],
                    modality=modality,
                    salary=None,
                    summary=description or "Sin descripción",
                    source=source.name,
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception as e:
        print(f"Error crawling The Muse: {e}")
    
    return offers


async def crawl_api_jsearch(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """Crawlea JSearch API (RapidAPI - requiere API key)."""
    offers: list[JobOffer] = []
    api_key = os.getenv(source.api_key_env, "")
    
    if not api_key:
        return offers
    
    try:
        search_query = query if query else "developer"
        if location:
            search_query = f"{search_query} {location}"
            
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }
        params = {
            "query": search_query,
            "num_pages": 2,
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(source.endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
        jobs = data.get("data", [])
        
        for job in jobs[:100]:
            title = job.get("job_title", "Vacante")
            company = job.get("employer_name", "Empresa")
            city = job.get("job_city", "")
            country = job.get("job_country", "")
            state = job.get("job_state", "")
            description = _clean_text(job.get("job_description", ""))
            url = job.get("job_apply_link", "")
            is_remote = job.get("job_is_remote", False)
            
            salary_min = job.get("job_min_salary")
            salary_max = job.get("job_max_salary")
            salary = None
            if salary_min and salary_max:
                salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                salary = f"${salary_min:,.0f}+"
            
            if not url:
                continue
            
            full_location = f"{city}, {state}" if state else city
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, city, url),
                    title=title,
                    company=company,
                    country=country if country else "Global",
                    city=full_location if full_location else ("Remoto" if is_remote else ""),
                    modality="Remoto" if is_remote else "Presencial",
                    salary=salary,
                    summary=description or "Sin descripción",
                    source=source.name,
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception as e:
        print(f"Error crawling JSearch: {e}")
    
    return offers


async def crawl_html_generic(source: SourceConfig, query: str = "", location: str = "") -> list[JobOffer]:
    """
    Crawler genérico para portales HTML.
    Usa heurísticas para detectar ofertas de trabajo en páginas web.
    """
    offers: list[JobOffer] = []
    
    try:
        url = source.endpoint
        if "{query}" in url:
            url = url.replace("{query}", quote_plus(query) if query else "")
        if "{location}" in url:
            url = url.replace("{location}", quote_plus(location) if location else "")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_selectors = [
            "article.job", "div.job-listing", "li.job-item",
            "div.vacancy", "div.offer", "article.offer",
            "div.job-card", "div.job_listing", "div.empleo",
            "div.oferta", "li.oferta", "article.empleo",
            "[data-job]", "[data-vacancy]", "[class*='job']",
            "[class*='empleo']", "[class*='oferta']", "[class*='vacancy']",
        ]
        
        job_elements = []
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                job_elements.extend(elements[:30])
                if len(job_elements) >= 30:
                    break
        
        if not job_elements:
            links = soup.find_all("a", href=True)
            job_links = [
                link for link in links
                if any(kw in link.get("href", "").lower() for kw in ["empleo", "trabajo", "job", "vacancy", "oferta"])
            ]
            job_elements = job_links[:30]
        
        query_lower = query.lower() if query else ""
        location_lower = location.lower() if location else ""
        
        seen_urls: set[str] = set()
        
        for element in job_elements:
            try:
                link = element.find("a", href=True) if element.name != "a" else element
                if not link:
                    continue
                    
                job_url = link.get("href", "")
                if not job_url or job_url in seen_urls:
                    continue
                    
                if not job_url.startswith("http"):
                    job_url = urljoin(source.endpoint, job_url)
                
                seen_urls.add(job_url)
                
                title_elem = element.find(["h1", "h2", "h3", "h4", "a", "span"], class_=lambda x: x and any(
                    kw in str(x).lower() for kw in ["title", "titulo", "nombre", "puesto", "cargo"]
                ))
                title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
                
                if not title or len(title) < 5:
                    continue
                
                company_elem = element.find(["span", "div", "a"], class_=lambda x: x and any(
                    kw in str(x).lower() for kw in ["company", "empresa", "employer", "compañia"]
                ))
                company = company_elem.get_text(strip=True) if company_elem else _extract_company(source.name, title)
                
                location_elem = element.find(["span", "div"], class_=lambda x: x and any(
                    kw in str(x).lower() for kw in ["location", "ubicacion", "lugar", "ciudad", "city"]
                ))
                job_location = location_elem.get_text(strip=True) if location_elem else ""
                
                full_text = element.get_text(" ", strip=True)
                
                if query_lower and query_lower not in full_text.lower():
                    continue
                
                city, country = _detect_city_country(f"{full_text} {job_location}", source.country_hint)
                
                if location_lower:
                    if location_lower not in f"{city} {country} {job_location}".lower():
                        continue
                
                modality = _detect_modality(full_text)
                salary = _extract_salary(full_text)
                summary = _clean_text(full_text, 200)
                
                offers.append(
                    JobOffer(
                        id=_canonical_id(title, company, city, job_url),
                        title=title[:150],
                        company=company[:100] if company else source.name,
                        country=country if country else source.country_hint,
                        city=city if city else job_location[:50] if job_location else "",
                        modality=modality,
                        salary=salary,
                        summary=summary or "Ver detalles en el sitio web",
                        source=source.name,
                        url=job_url,
                        published_at=_now_label(),
                    )
                )
                
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error crawling HTML {source.name}: {e}")
    
    return offers


# =============================================================================
# MOTOR PRINCIPAL DE BÚSQUEDA
# =============================================================================

async def search_source(source: SourceConfig, query: str, location: str) -> list[JobOffer]:
    """Busca en una fuente específica según su tipo."""
    if source.kind == "rss":
        return await crawl_rss(source, query, location)
    elif source.kind == "api":
        if "arbeitnow" in source.name.lower():
            return await crawl_api_arbeitnow(source, query, location)
        elif "remotive" in source.name.lower():
            return await crawl_api_remotive(source, query, location)
        elif "muse" in source.name.lower():
            return await crawl_api_themuse(source, query, location)
        elif "jsearch" in source.name.lower():
            return await crawl_api_jsearch(source, query, location)
        else:
            return []
    elif source.kind == "html":
        return await crawl_html_generic(source, query, location)
    else:
        return []


async def search_all_sources(
    query: str = "",
    country: str = "",
    city: str = "",
    max_sources: int = 15,
) -> list[JobOffer]:
    """
    Motor de búsqueda principal - busca en múltiples fuentes en paralelo.
    Prioriza fuentes del país del usuario.
    """
    location = f"{city} {country}".strip() if city or country else ""
    
    if country:
        sources = get_sources_by_country(country)[:max_sources]
    else:
        sources = sorted(ALL_SOURCES, key=lambda s: s.priority)[:max_sources]
    
    tasks = [search_source(source, query, location) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_offers: list[JobOffer] = []
    for result in results:
        if isinstance(result, list):
            all_offers.extend(result)
    
    return all_offers


def crawl_all_sources() -> list[JobOffer]:
    """
    Versión síncrona para compatibilidad con código existente.
    """
    return asyncio.run(search_all_sources())


async def search_jobs_async(
    query: str = "",
    country: str = "",
    city: str = "",
) -> list[JobOffer]:
    """
    Función principal de búsqueda asíncrona.
    """
    return await search_all_sources(query, country, city)
