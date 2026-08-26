"""
Dynamic Suggestion Service:
Generates categorized suggestions, area chips, and pincode lists based on parsed search queries.
"""

from typing import Dict, List, Any, Optional
from .geo_data import (
    CITY_DATABASE,
    get_areas_for_city,
    get_pincodes_for_city_area,
    get_city_info
)

# Common category suggestions for entity types
ENTITY_SUGGESTIONS = {
    "restaurant": [
        {"id": "all", "label": "All Restaurants", "type": "category"},
        {"id": "pure_veg", "label": "Pure Veg Restaurants", "type": "food_type", "value": "pure_veg"},
        {"id": "veg", "label": "Veg Restaurants", "type": "food_type", "value": "veg"},
        {"id": "non_veg", "label": "Non-Veg Restaurants", "type": "food_type", "value": "non_veg"},
        {"id": "cafes", "label": "Cafes & Coffee Shops", "type": "category", "value": "Cafe"},
        {"id": "fast_food", "label": "Fast Food Restaurants", "type": "category", "value": "Fast Food"},
        {"id": "family", "label": "Family Restaurants", "type": "category", "value": "Family Restaurant"},
        {"id": "fine_dining", "label": "Fine Dining", "type": "category", "value": "Fine Dining"},
        {"id": "multi_cuisine", "label": "Multi-Cuisine Restaurants", "type": "category", "value": "Multi-Cuisine"},
        {"id": "rooftop", "label": "Rooftop Restaurants", "type": "category", "value": "Rooftop"},
        {"id": "bakery", "label": "Bakeries & Desserts", "type": "category", "value": "Bakery"}
    ],
    "hospital": [
        {"id": "all", "label": "All Hospitals", "type": "category"},
        {"id": "multi_spec", "label": "Multi-Speciality Hospitals", "type": "speciality", "value": "Multi-Speciality"},
        {"id": "general", "label": "General Hospitals", "type": "speciality", "value": "General Hospital"},
        {"id": "dental", "label": "Dental Hospitals / Clinics", "type": "speciality", "value": "Dental"},
        {"id": "pediatric", "label": "Children's Hospitals (Pediatric)", "type": "speciality", "value": "Pediatric"},
        {"id": "women", "label": "Women's / Maternity Hospitals", "type": "speciality", "value": "Women"},
        {"id": "eye", "label": "Eye Hospitals (Ophthalmology)", "type": "speciality", "value": "Eye"},
        {"id": "heart", "label": "Heart / Cardiology Hospitals", "type": "speciality", "value": "Heart"},
        {"id": "orthopedic", "label": "Orthopedic Hospitals", "type": "speciality", "value": "Orthopedic"},
        {"id": "cancer", "label": "Cancer Hospitals (Oncology)", "type": "speciality", "value": "Cancer"},
        {"id": "ent", "label": "ENT Clinics & Hospitals", "type": "speciality", "value": "ENT"},
        {"id": "govt", "label": "Government Hospitals", "type": "speciality", "value": "Government"},
        {"id": "private", "label": "Private Hospitals", "type": "speciality", "value": "Private"}
    ],
    "gas_station": [
        {"id": "all", "label": "All Gas Stations", "type": "category"},
        {"id": "petrol_pump", "label": "Petrol Pumps", "type": "category", "value": "Petrol Pump"},
        {"id": "ev_charging", "label": "EV Charging Stations", "type": "category", "value": "EV Charging"},
        {"id": "24_hours", "label": "24 Hours Fuel Stations", "type": "category", "value": "24 Hours"}
    ],
    "hotel": [
        {"id": "all", "label": "All Hotels", "type": "category"},
        {"id": "luxury", "label": "5-Star & Luxury Hotels", "type": "category", "value": "Luxury"},
        {"id": "budget", "label": "Budget Hotels", "type": "category", "value": "Budget"},
        {"id": "resort", "label": "Resorts", "type": "category", "value": "Resort"},
        {"id": "business", "label": "Business Hotels", "type": "category", "value": "Business"}
    ],
    "school": [
        {"id": "all", "label": "All Schools", "type": "category"},
        {"id": "cbse", "label": "CBSE Schools", "type": "category", "value": "CBSE"},
        {"id": "icse", "label": "ICSE Schools", "type": "category", "value": "ICSE"},
        {"id": "international", "label": "International Schools", "type": "category", "value": "International"},
        {"id": "play_school", "label": "Play Schools & Pre-Schools", "type": "category", "value": "Play School"}
    ],
    "gym": [
        {"id": "all", "label": "All Gyms & Fitness", "type": "category"},
        {"id": "crossfit", "label": "Crossfit Centers", "type": "category", "value": "Crossfit"},
        {"id": "unisex", "label": "Unisex Gyms", "type": "category", "value": "Unisex Gym"},
        {"id": "yoga", "label": "Yoga & Pilates Studios", "type": "category", "value": "Yoga"}
    ],
    "salon": [
        {"id": "all", "label": "All Salons & Spas", "type": "category"},
        {"id": "beauty_parlour", "label": "Beauty Parlours", "type": "category", "value": "Beauty Parlour"},
        {"id": "men_salon", "label": "Men's Hair Salons", "type": "category", "value": "Men's Salon"},
        {"id": "spa", "label": "Luxury Spas & Massage", "type": "category", "value": "Spa"}
    ],
    "pharmacy": [
        {"id": "all", "label": "All Pharmacies", "type": "category"},
        {"id": "24x7", "label": "24x7 Medical Stores", "type": "category", "value": "24x7"},
        {"id": "generic", "label": "Generic Medicine Stores", "type": "category", "value": "Generic Medicine"}
    ]
}

def generate_suggestions(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Generates categories, area chips, and pincode/postcode suggestions."""
    entity = parsed.get("entity_type", "restaurant")
    city = parsed.get("city", "")
    area = parsed.get("area", "")
    country = parsed.get("country", "India")
    postal_label = parsed.get("postal_label", "Pincode")

    categories = ENTITY_SUGGESTIONS.get(entity, [
        {"id": "all", "label": f"All {entity.title()}s", "type": "category"}
    ])

    areas = []
    if city:
        areas = get_areas_for_city(city)

    pincodes = []
    if city:
        pincodes = get_pincodes_for_city_area(city, area)
    elif parsed.get("pincode"):
        pincodes = [parsed["pincode"]]

    return {
        "entity_type": entity,
        "country": country,
        "postal_label": postal_label,
        "city": city,
        "area": area,
        "categories": categories,
        "areas": areas,
        "pincodes": pincodes
    }
