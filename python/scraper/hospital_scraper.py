"""
Hospital Scraper:
Dynamic postcode-by-postcode Google Maps hospital and clinic scraper.
Supports doctor listing extraction and immediate disk CSV writing.
"""

import re
from typing import Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .bs4_parser import clean_text

def extract_doctor_name(text: str) -> str:
    match = re.search(r"\b(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", text)
    if match:
        return clean_text(match.group(1))
    return ""

class HospitalScraper(BaseScraper):
    def get_entity_type(self) -> str:
        return "hospital"

    def extract_listing_details(
        self,
        soup: BeautifulSoup,
        full_text: str,
        href: str,
        listing_label: str,
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        record = super().extract_listing_details(soup, full_text, href, listing_label, item)
        record["entity_type"] = "hospital"

        speciality = item.get("speciality", "") or record.get("category", "")
        record["speciality"] = speciality
        record["doctor_name"] = extract_doctor_name(full_text)
        record["doctor_speciality"] = speciality

        return record
