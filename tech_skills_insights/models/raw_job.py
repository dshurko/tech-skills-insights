from dataclasses import dataclass
from datetime import date


@dataclass
class RawJob:
    id: int
    title: str
    company: str
    category: str
    description: str
    published_at: date
    url: str
    source: str
