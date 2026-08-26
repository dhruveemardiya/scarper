"""
Generic Multi-Level Location & Postcode Resolution Service:
Provides country-aware, 5-level cascading postal code resolution for ANY city/area worldwide.

Priority:
  Level 1: Local curated dataset & persistent cache (data/postal_cache.json)
  Level 2: Area / Neighborhood mapping
  Level 3: Live Postal Code / Geocoding APIs (India Post / Nominatim / Zippopotam / Postcodes.io)
  Level 4: Search Result Address PIN Extractor
  Level 5: Graceful fallback for manual addition (+ Add Pincode) & direct search

Features:
  - Country-specific format validation (India 6-digit, UK alphanumeric, US 5-digit, etc.)
  - Deduplication, normalization, sorting
  - Source tracking (LOCAL_DATASET, AREA_MAPPING, POSTCODE_SERVICE, ADDRESS_EXTRACTION, CACHE, MANUAL)
"""

import os
import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from .geo_data import CITY_DATABASE, normalize_city_key

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CACHE_FILE = os.path.join(CACHE_DIR, "postal_cache.json")

# In-Memory Cache
_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}

def _load_disk_cache():
    global _MEMORY_CACHE
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
        except Exception:
            pass
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _MEMORY_CACHE = json.load(f)
        except Exception:
            _MEMORY_CACHE = {}

def _save_disk_cache():
    try:
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_MEMORY_CACHE, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# Initialize cache
_load_disk_cache()


def validate_postcode(postcode: str, country: str = "India") -> bool:
    """Country-aware postal code format validator."""
    if not postcode or not isinstance(postcode, str):
        return False
    clean = postcode.strip()
    c_upper = country.upper()

    if c_upper == "INDIA":
        # Indian PIN: 6 digits, first digit 1-9
        return bool(re.match(r"^[1-9]\d{5}$", clean))
    elif c_upper == "UK":
        # UK Postcode: alphanumeric e.g. SW1A 1AA, EC1, LE18, M1, etc.
        return bool(re.match(r"^[A-Z]{1,2}\d[A-Z\d]?(\s*\d?[A-Z]{0,2})?$", clean, re.IGNORECASE))
    elif c_upper == "USA" or c_upper == "US":
        # US ZIP: 5 digits or ZIP+4
        return bool(re.match(r"^\d{5}(-\d{4})?$", clean))
    else:
        # Generic alphanumeric postal code (3 to 10 chars)
        return bool(re.match(r"^[A-Z0-9 -]{3,10}$", clean, re.IGNORECASE))


def normalize_postcodes(postcodes: List[str], country: str = "India") -> List[str]:
    """Cleans, validates, deduplicates, and sorts postal codes."""
    valid_set = set()
    for p in postcodes:
        if not p:
            continue
        cleaned = str(p).strip()
        if country.upper() == "UK":
            cleaned = cleaned.upper()
        if validate_postcode(cleaned, country):
            valid_set.add(cleaned)
    return sorted(list(valid_set))


def resolve_postcodes(
    country: str = "India",
    state: str = "",
    city: str = "",
    area: str = "",
    query: str = ""
) -> Dict[str, Any]:
    """
    Main Multi-Level Postcode Resolver.
    Returns:
      {
        "country": str,
        "state": str,
        "city": str,
        "area": str,
        "postal_label": str,
        "postcodes": List[str],
        "source": str,
        "confidence": float
      }
    """
    clean_country = country.strip() if country else "India"
    clean_city = city.strip()
    clean_area = area.strip()
    postal_label = "Postcode" if clean_country.upper() == "UK" else "Pincode"

    cache_key = f"{clean_country.lower()}:{clean_city.lower()}:{clean_area.lower()}"

    # ----------------------------------------------------
    # LEVEL 0: In-Memory / Local Disk Cache
    # ----------------------------------------------------
    if cache_key in _MEMORY_CACHE and _MEMORY_CACHE[cache_key].get("postcodes"):
        cached = _MEMORY_CACHE[cache_key]
        return {
            "country": cached.get("country", clean_country),
            "state": cached.get("state", state),
            "city": cached.get("city", clean_city),
            "area": cached.get("area", clean_area),
            "postal_label": postal_label,
            "postcodes": cached["postcodes"],
            "source": "CACHE",
            "confidence": 0.95
        }

    # ----------------------------------------------------
    # LEVEL 1: Curated Local Geo Database (CITY_DATABASE)
    # ----------------------------------------------------
    city_key = normalize_city_key(clean_city)
    if city_key in CITY_DATABASE:
        city_info = CITY_DATABASE[city_key]
        detected_country = city_info.get("country", clean_country)
        detected_state = city_info.get("state", state)

        # Level 2 check inside city (Area mapping)
        if clean_area and clean_area.lower() not in ["all", ""]:
            for area_name, pins in city_info.get("areas", {}).items():
                if clean_area.lower() in area_name.lower() or area_name.lower() in clean_area.lower():
                    norm_pins = normalize_postcodes(pins, detected_country)
                    if norm_pins:
                        result = {
                            "country": detected_country,
                            "state": detected_state,
                            "city": city_info.get("name", clean_city),
                            "area": area_name,
                            "postal_label": postal_label,
                            "postcodes": norm_pins,
                            "source": "AREA_MAPPING",
                            "confidence": 0.98
                        }
                        _MEMORY_CACHE[cache_key] = result
                        _save_disk_cache()
                        return result

        # Collect all city pincodes
        all_pins = set()
        if "pincodes" in city_info:
            all_pins.update(city_info["pincodes"])
        for pins in city_info.get("areas", {}).values():
            all_pins.update(pins)

        norm_pins = normalize_postcodes(list(all_pins), detected_country)
        if norm_pins:
            result = {
                "country": detected_country,
                "state": detected_state,
                "city": city_info.get("name", clean_city),
                "area": clean_area,
                "postal_label": postal_label,
                "postcodes": norm_pins,
                "source": "LOCAL_DATASET",
                "confidence": 0.95
            }
            _MEMORY_CACHE[cache_key] = result
            _save_disk_cache()
            return result

    # ----------------------------------------------------
    # LEVEL 3: Live Geocoding / Postal Code API Resolution
    # (Fast, non-blocking HTTP lookup with timeout)
    # ----------------------------------------------------
    api_pins = _fetch_live_postcodes(clean_country, clean_city, clean_area)
    if api_pins:
        norm_pins = normalize_postcodes(api_pins, clean_country)
        if norm_pins:
            result = {
                "country": clean_country,
                "state": state,
                "city": clean_city.title(),
                "area": clean_area,
                "postal_label": postal_label,
                "postcodes": norm_pins,
                "source": "POSTCODE_SERVICE",
                "confidence": 0.90
            }
            _MEMORY_CACHE[cache_key] = result
            _save_disk_cache()
            return result

    # ----------------------------------------------------
    # LEVEL 4: Address / Query PIN Code Extraction
    # ----------------------------------------------------
    if query:
        extracted = _extract_pins_from_text(query, clean_country)
        if extracted:
            norm_pins = normalize_postcodes(extracted, clean_country)
            if norm_pins:
                return {
                    "country": clean_country,
                    "state": state,
                    "city": clean_city.title() if clean_city else "",
                    "area": clean_area,
                    "postal_label": postal_label,
                    "postcodes": norm_pins,
                    "source": "ADDRESS_EXTRACTION",
                    "confidence": 0.85
                }

    # ----------------------------------------------------
    # LEVEL 5: Fallback (Empty list -> UI shows manual Add)
    # ----------------------------------------------------
    return {
        "country": clean_country,
        "state": state,
        "city": clean_city.title() if clean_city else "",
        "area": clean_area,
        "postal_label": postal_label,
        "postcodes": [],
        "source": "FALLBACK",
        "confidence": 0.0
    }


def _extract_pins_from_text(text: str, country: str = "India") -> List[str]:
    """Extracts valid postal codes from text via country-specific regex."""
    if not text:
        return []
    pins = []
    if country.upper() == "INDIA":
        matches = re.findall(r"\b([1-9]\d{5})\b", text)
        pins.extend(matches)
    elif country.upper() == "UK":
        matches = re.findall(r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d?[A-Z]{0,2})\b", text, re.IGNORECASE)
        pins.extend([m.upper() for m in matches])
    elif country.upper() in ["USA", "US"]:
        matches = re.findall(r"\b(\d{5})\b", text)
        pins.extend(matches)
    return pins


def _fetch_live_postcodes(country: str, city: str, area: str = "") -> List[str]:
    """
    Queries live public geo/postal endpoints (Zippopotam, Nominatim / India Post API)
    with a short 2.5s timeout.
    """
    if not city or len(city) < 3:
        return []

    results = []

    # 1. India: Postal Pincode API
    if country.upper() == "INDIA":
        try:
            # India Post Public API Endpoint
            encoded_city = urllib.parse.quote(city.strip())
            url = f"https://api.postalpincode.in/postoffice/{encoded_city}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DataScraper-Desktop/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0:
                        po_list = data[0].get("PostOffice", [])
                        if po_list:
                            for po in po_list:
                                pin = po.get("Pincode")
                                if pin:
                                    results.append(str(pin).strip())
                            if results:
                                return results
        except Exception:
            pass

    # 2. UK: Postcodes.io API
    elif country.upper() == "UK":
        try:
            encoded_city = urllib.parse.quote(city.strip())
            url = f"https://api.postcodes.io/places?q={encoded_city}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DataScraper-Desktop/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    places = data.get("result", [])
                    for p in places:
                        outcode = p.get("outcode")
                        if outcode:
                            results.append(outcode)
                    if results:
                        return results
        except Exception:
            pass

    # 3. Zippopotam.us Global Postal API (Supports US, DE, FR, GB, IN, etc.)
    country_code_map = {
        "INDIA": "in",
        "UK": "gb",
        "USA": "us",
        "US": "us",
        "GERMANY": "de",
        "FRANCE": "fr",
        "CANADA": "ca",
        "AUSTRALIA": "au"
    }
    cc = country_code_map.get(country.upper(), "in")
    try:
        encoded_city = urllib.parse.quote(city.strip())
        url = f"https://api.zippopotam.us/{cc}/{encoded_city}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DataScraper-Desktop/1.0"}
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                places = data.get("places", [])
                for pl in places:
                    code = pl.get("post code")
                    if code:
                        results.append(str(code).strip())
                if results:
                    return results
    except Exception:
        pass

    return results
