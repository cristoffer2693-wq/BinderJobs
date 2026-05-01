from __future__ import annotations

from pydantic import BaseModel


class JobOffer(BaseModel):
    id: str
    title: str
    company: str
    country: str
    city: str
    modality: str = "No especificado"
    salary: str | None = None
    summary: str
    source: str
    url: str
    published_at: str
    score: float = 0.0
