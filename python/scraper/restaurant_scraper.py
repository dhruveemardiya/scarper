"""
Restaurant Scraper:
Dynamic postcode-by-postcode Google Maps restaurant scraper using deep feed scrolling and detailed listing extraction.
Appends each record immediately to the disk CSV.
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class RestaurantScraper(BaseScraper):
    def get_entity_type(self) -> str:
        return "restaurant"

    def extract_listing_details(
        self,
        soup: BeautifulSoup,
        full_text: str,
        href: str,
        listing_label: str,
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        record = super().extract_listing_details(soup, full_text, href, listing_label, item)
        record["entity_type"] = "restaurant"

        food_type = item.get("food_type", "all")
        name = record.get("name", "")
        category = record.get("category", "")
        full_lower = f"{name} {category} {full_text}".lower()

        # Price Range
        price_range = ""
        if "₹₹₹₹" in full_text or "$$$$" in full_text:
            price_range = "₹₹₹₹ (Very Expensive)"
        elif "₹₹₹" in full_text or "$$$" in full_text:
            price_range = "₹₹₹ (Expensive)"
        elif "₹₹" in full_text or "$$" in full_text:
            price_range = "₹₹ (Moderate)"
        elif "₹" in full_text or "$" in full_text:
            price_range = "₹ (Inexpensive)"
        record["price_range"] = price_range

        # Veg / Non-Veg detection
        veg_val = food_type
        if "pure veg" in full_lower or "jain" in full_lower:
            veg_val = "pure_veg"
        elif "non-veg" in full_lower or "chicken" in full_lower or "mutton" in full_lower or "biryani" in full_lower:
            veg_val = "non_veg"
        elif "veg" in full_lower and veg_val == "all":
            veg_val = "veg"
        record["veg_type"] = veg_val

        return record
