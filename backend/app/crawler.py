from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup

from .models import JobOffer


def _canonical_id(title: str, company: str, url: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _clean_text(text: str, max_length: int = 300) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(" ", strip=True)
    return clean[:max_length] if len(clean) > max_length else clean


def crawl_rss_remoteok() -> list[JobOffer]:
    """Crawlea RemoteOK RSS."""
    offers: list[JobOffer] = []
    try:
        parsed = feedparser.parse("https://remoteok.com/remote-jobs.rss")
        for entry in parsed.entries[:30]:
            title = entry.get("title", "Vacante")
            link = entry.get("link", "")
            if not link:
                continue
            summary = _clean_text(entry.get("summary", ""))
            company = title.split(" at ")[-1] if " at " in title else "RemoteOK"
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, link),
                    title=title,
                    company=company,
                    country="Global",
                    city="Remoto",
                    modality="Remoto",
                    salary=None,
                    summary=summary or "Ver detalles en el sitio",
                    source="RemoteOK",
                    url=link,
                    published_at=_now_label(),
                )
            )
    except Exception:
        pass
    return offers


def crawl_api_remotive() -> list[JobOffer]:
    """Crawlea Remotive API."""
    offers: list[JobOffer] = []
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://remotive.com/api/remote-jobs")
            response.raise_for_status()
            data = response.json()
            
        for job in data.get("jobs", [])[:30]:
            title = job.get("title", "Vacante")
            company = job.get("company_name", "Empresa")
            url = job.get("url", "")
            if not url:
                continue
            summary = _clean_text(job.get("description", ""))
            salary = job.get("salary", "")
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, url),
                    title=title,
                    company=company,
                    country="Global",
                    city="Remoto",
                    modality="Remoto",
                    salary=salary if salary else None,
                    summary=summary or "Ver detalles en el sitio",
                    source="Remotive",
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception:
        pass
    return offers


def crawl_api_arbeitnow() -> list[JobOffer]:
    """Crawlea Arbeitnow API."""
    offers: list[JobOffer] = []
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://www.arbeitnow.com/api/job-board-api")
            response.raise_for_status()
            data = response.json()
            
        for job in data.get("data", [])[:30]:
            title = job.get("title", "Vacante")
            company = job.get("company_name", "Empresa")
            url = job.get("url", "")
            if not url:
                continue
            summary = _clean_text(job.get("description", ""))
            remote = job.get("remote", False)
            location = job.get("location", "")
            
            offers.append(
                JobOffer(
                    id=_canonical_id(title, company, url),
                    title=title,
                    company=company,
                    country="Global" if remote else "Europa",
                    city="Remoto" if remote else location,
                    modality="Remoto" if remote else "Presencial",
                    salary=None,
                    summary=summary or "Ver detalles en el sitio",
                    source="Arbeitnow",
                    url=url,
                    published_at=_now_label(),
                )
            )
    except Exception:
        pass
    return offers


def crawl_all_sources() -> list[JobOffer]:
    """Crawlea todas las fuentes disponibles."""
    all_offers: list[JobOffer] = []
    
    all_offers.extend(crawl_rss_remoteok())
    all_offers.extend(crawl_api_remotive())
    all_offers.extend(crawl_api_arbeitnow())
    
    return all_offers
