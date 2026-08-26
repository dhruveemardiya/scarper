"""
NLP Query Parser:
Extracts entity type, country, city, area, pincode/postcode, category, speciality,
and resolved postal codes from ANY natural language queries dynamically.
"""

import re
from typing import Dict, Any, Optional, List
from .geo_data import (
    CITY_DATABASE,
    normalize_city_key,
    get_city_info,
    get_pincodes_for_city_area,
    find_city_by_area_or_pincode
)
from .postcode_resolver import resolve_postcodes, validate_postcode, normalize_postcodes

KNOWN_ENTITY_MAPPINGS = {
    "coaching": ["coaching institute", "coaching", "tuition", "classes", "training institute"],
    "school": ["school", "schools", "academy", "high school", "vidyalaya", "vidhyalay", "primary school"],
    "college": ["college", "colleges", "university", "institute", "campus"],
    "hospital": ["hospital", "hospitals", "clinic", "clinics", "doctor", "doctors", "healthcare", "dispensary", "nursing home", "medical center", "mediclinic"],
    "restaurant": ["restaurant", "restaurants", "cafe", "cafes", "diner", "eatery", "food", "dining", "bistro", "dhaba", "bakery", "restro", "sweets", "pizzeria", "burger"],
    "gas_station": ["gas station", "gas stations", "petrol pump", "petrol pumps", "fuel station", "fuel stations", "filling station", "ev charging"],
    "hotel": ["hotel", "hotels", "resort", "resorts", "motel", "lodge", "guest house", "stay"],
    "gym": ["gym", "gyms", "fitness center", "fitness club", "workout", "crossfit"],
    "salon": ["salon", "salons", "beauty parlour", "spa", "barber", "hair studio"],
    "pharmacy": ["pharmacy", "pharmacies", "chemist", "medical store", "drugstore"],
    "real_estate": ["real estate", "property", "realtor", "builders", "brokers"]
}

HOSPITAL_SPECIALITIES = [
    "Multi-Speciality", "Multi Speciality", "Multispeciality",
    "Dental", "Dentist", "Dental Clinic", "Eye", "Ophthalmology",
    "Heart", "Cardiology", "Cardiologist",
    "Orthopedic", "Orthopedics", "Bone",
    "Pediatric", "Pediatrics", "Children", "Child Specialist",
    "Gynecology", "Gynecologist", "Maternity", "Women",
    "Neurology", "Neurologist", "Nephrology", "Kidney",
    "ENT", "Ear Nose Throat",
    "Skin", "Dermatology", "Dermatologist",
    "General Hospital", "General Medicine",
    "Cancer", "Oncology", "Urology", "Gastroenterology", "Ayurvedic", "Homeopathic"
]

def parse_search_query(query: str) -> Dict[str, Any]:
    """
    Parses natural language query for any business/entity type and location:
    e.g. 'school in Ahmedabad', 'dental clinic in Satellite Road Ahmedabad', 'solar panel dealer in Rajkot'
    """
    cleaned = query.strip()
    q_lower = cleaned.lower()

    # 1. Detect Country
    country = "India"
    if re.search(r"\b(uk|u\.k\.|united kingdom|england|britain|great britain|london|leicester|sheffield|birmingham|manchester)\b", q_lower):
        country = "UK"

    # 2. Detect Direct Pincode / Postcode
    detected_pincode = ""
    pin_match = re.search(r"\b(\d{6})\b", cleaned)
    if pin_match:
        detected_pincode = pin_match.group(1)
    else:
        uk_match = re.search(r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d?[A-Z]{0,2})\b", cleaned, re.IGNORECASE)
        if uk_match and country == "UK":
            detected_pincode = uk_match.group(1).upper()

    # 3. Detect City & Area
    detected_city = ""
    detected_area = ""

    # Check known cities in CITY_DATABASE
    for city_key, city_data in CITY_DATABASE.items():
        city_name = city_data["name"]
        if re.search(rf"\b{re.escape(city_key)}\b", q_lower) or re.search(rf"\b{re.escape(city_name.lower())}\b", q_lower):
            detected_city = city_name
            country = city_data.get("country", country)
            # Check areas of this city
            for area in city_data.get("areas", {}).keys():
                if re.search(rf"\b{re.escape(area.lower())}\b", q_lower):
                    detected_area = area
                    break
            break

    # If city not found by name, check by pincode or area
    if not detected_city and detected_pincode:
        geo_info = find_city_by_area_or_pincode(detected_pincode)
        if geo_info:
            detected_city = geo_info["city"]
            country = geo_info.get("country", country)
            detected_area = geo_info.get("area", "")

    if not detected_city:
        for word in q_lower.split():
            geo_info = find_city_by_area_or_pincode(word)
            if geo_info:
                detected_city = geo_info["city"]
                country = geo_info.get("country", country)
                detected_area = geo_info.get("area", "")
                break

    # Dynamic location fallback from prepositions (e.g. 'school in Junagadh', 'hotel in Keshod')
    if not detected_city:
        loc_match = re.search(r"\b(?:in|near|at|around)\s+([a-zA-Z\s]+)", cleaned, re.IGNORECASE)
        if loc_match:
            cand = loc_match.group(1).strip()
            cand_clean = re.sub(r"\b(india|uk|united kingdom|usa|gujarat|maharashtra|rajasthan)\b", "", cand, flags=re.IGNORECASE).strip()
            if cand_clean and len(cand_clean) >= 3 and cand_clean.lower() not in ["the", "all", "best", "top", "good", "city"]:
                detected_city = cand_clean.title()

    # 4. Detect Entity Type & Entity Label Dynamically
    detected_entity = ""
    entity_label = ""

    # Check known entity triggers first
    for ent, triggers in KNOWN_ENTITY_MAPPINGS.items():
        if any(re.search(rf"\b{re.escape(t)}\b", q_lower) for t in triggers):
            detected_entity = ent
            entity_label = ent.replace("_", " ").title()
            break

    # Detect Speciality (e.g. Dental Clinic, Eye Hospital)
    detected_speciality = ""
    for spec in HOSPITAL_SPECIALITIES:
        pattern = rf"\b{re.escape(spec.lower()).replace(' ', '[- ]?')}\b"
        if re.search(pattern, q_lower):
            detected_speciality = spec
            if not detected_entity or detected_entity == "business":
                detected_entity = "hospital"
                entity_label = f"{spec} Clinic" if "clinic" in q_lower else f"{spec} Hospital"
            break

    # If entity is still unknown or generic, dynamically extract entity phrase
    if not detected_entity:
        entity_raw = cleaned
        # Strip location prepositions and location tokens
        location_patterns = [
            r"\b(in|of|at|near|around|beside|across)\s+.*$",
            r"\b(ahmedabad|rajkot|surat|vadodara|mumbai|delhi|bangalore|london|leicester|sheffield|birmingham|manchester|uk|india|gujarat)\b",
            r"\b\d{6}\b"
        ]
        for pat in location_patterns:
            entity_raw = re.sub(pat, "", entity_raw, flags=re.IGNORECASE)
        
        entity_raw = entity_raw.strip(" ,.-/")
        if entity_raw:
            entity_label = entity_raw.title()
            detected_entity = re.sub(r"[^a-z0-9]+", "_", entity_raw.lower()).strip("_")
        else:
            detected_entity = "business"
            entity_label = "Business"

    if not entity_label:
        entity_label = detected_entity.replace("_", " ").title()

    # 5. Resolve Pincodes / Postcodes using Multi-Level Postcode Resolver
    postal_res = resolve_postcodes(
        country=country,
        state="",
        city=detected_city,
        area=detected_area,
        query=cleaned
    )
    resolved_pincodes = postal_res.get("postcodes", [])
    postal_label = postal_res.get("postal_label", "Postcode" if country == "UK" else "Pincode")
    postcode_source = postal_res.get("source", "LOCAL")

    # If direct pincode was explicitly typed by user in query, ensure it is included
    if detected_pincode and detected_pincode not in resolved_pincodes:
        resolved_pincodes = [detected_pincode] + resolved_pincodes

    # Keyword extraction
    rem = q_lower
    for stop_word in ["of", "in", "near", "at", "the", "pure", "veg", "non", "all", "best", "top"]:
        rem = re.sub(rf"\b{re.escape(stop_word)}\b", "", rem)
    if detected_city:
        rem = re.sub(rf"\b{re.escape(detected_city.lower())}\b", "", rem)
    if detected_area:
        rem = re.sub(rf"\b{re.escape(detected_area.lower())}\b", "", rem)
    if detected_pincode:
        rem = re.sub(rf"\b{re.escape(detected_pincode.lower())}\b", "", rem)
    rem_keyword = " ".join(rem.split()).strip()

    return {
        "raw_query": cleaned,
        "entity_type": detected_entity,
        "entity_label": entity_label,
        "country": country,
        "postal_label": postal_label,
        "city": detected_city,
        "area": detected_area,
        "pincode": detected_pincode,
        "category": "",
        "speciality": detected_speciality,
        "food_type": "all",
        "keyword": rem_keyword,
        "resolved_pincodes": resolved_pincodes,
        "postcode_source": postcode_source
    }
