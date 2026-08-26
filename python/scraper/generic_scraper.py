"""
Generic Scraper:
Dynamic postcode-by-postcode Google Maps generic business scraper (hotels, schools, coaching, gyms, etc.).
Appends each record immediately to the disk CSV.
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class GenericScraper(BaseScraper):
    def get_entity_type(self) -> str:
        return "business"
