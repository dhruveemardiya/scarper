"""
Comprehensive Automated Test Suite for Python Scraper Services (Final Requirements)
"""

import os
import sys
import tempfile
import json
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.nlp_parser import parse_search_query
from services.geo_data import get_pincodes_for_city_area
from services.csv_export import (
    ensure_csv_file_initialized,
    append_record_to_csv,
    write_all_records_to_csv,
    get_csv_headers,
    get_schema_columns
)
from scraper.duplicate_detector import DuplicateDetector
from scraper.hospital_scraper import extract_doctor_name

def test_dynamic_nlp_parser():
    print("=== Testing Dynamic NLP Query Parser (Arbitrary Queries) ===")
    
    # 1. School in Ahmedabad
    q1 = parse_search_query("school in Ahmedabad")
    assert q1["entity_type"] == "school"
    assert q1["entity_label"] == "School"
    assert q1["city"] == "Ahmedabad"
    assert q1["country"] == "India"
    assert len(q1["resolved_pincodes"]) >= 10
    print(f"  [PASS] 'school in Ahmedabad' -> {q1['entity_label']}, {q1['city']} ({len(q1['resolved_pincodes'])} pincodes)")

    # 2. Schools in Ahmedabad
    q2 = parse_search_query("schools in Ahmedabad")
    assert q2["entity_type"] == "school"
    assert q2["city"] == "Ahmedabad"
    print("  [PASS] 'schools in Ahmedabad' -> School in Ahmedabad")

    # 3. Dental clinic in Satellite Road Ahmedabad
    q3 = parse_search_query("dental clinic in Satellite Road Ahmedabad")
    assert q3["city"] == "Ahmedabad"
    assert "Satellite" in q3["area"]
    assert "380015" in q3["resolved_pincodes"]
    print(f"  [PASS] 'dental clinic in Satellite Road Ahmedabad' -> Area {q3['area']}, Pincodes {q3['resolved_pincodes']}")

    # 4. Hospitals in Rajkot
    q4 = parse_search_query("hospitals in Rajkot")
    assert q4["entity_type"] == "hospital"
    assert q4["city"] == "Rajkot"
    assert "360001" in q4["resolved_pincodes"]
    print("  [PASS] 'hospitals in Rajkot' -> Hospital in Rajkot")

    # 5. Gas stations in UK
    q5 = parse_search_query("gas stations in UK")
    assert q5["entity_type"] == "gas_station"
    assert q5["country"] == "UK"
    assert q5["postal_label"] == "Postcode"
    print("  [PASS] 'gas stations in UK' -> gas_station in UK with Postcode label")

    # 6. Solar panel dealer in Rajkot (arbitrary custom entity)
    q6 = parse_search_query("solar panel dealer in Rajkot")
    assert "solar" in q6["entity_type"]
    assert q6["city"] == "Rajkot"
    assert len(q6["resolved_pincodes"]) >= 5
    print(f"  [PASS] 'solar panel dealer in Rajkot' -> {q6['entity_label']} in {q6['city']}")

    # 7. Coaching institute in Rajkot
    q7 = parse_search_query("coaching institute in Rajkot")
    assert q7["city"] == "Rajkot"
    print(f"  [PASS] 'coaching institute in Rajkot' -> {q7['entity_label']} in {q7['city']}")

    # 8. Schools near 380015 (direct pincode in query)
    q8 = parse_search_query("schools near 380015")
    assert q8["pincode"] == "380015"
    assert "380015" in q8["resolved_pincodes"]
    print("  [PASS] 'schools near 380015' -> Direct Pincode 380015 resolved")

def test_dynamic_csv_and_custom_fields():
    print("\n=== Testing Dynamic CSV Schemas & Custom Fields ===")
    
    # Test School Schema
    school_headers = get_csv_headers("school", ["School Board", "Principal"])
    assert "School Name" in school_headers
    assert "School Board" in school_headers
    assert "Principal" in school_headers
    print("  [PASS] School schema + custom fields verified")

    temp_csv = os.path.join(tempfile.gettempdir(), f"test_scraper_{os.getpid()}.csv")
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

    try:
        ensure_csv_file_initialized(temp_csv, "school", ["School Board", "Principal"])
        rec = {
            "name": "Delhi Public School",
            "category": "CBSE School",
            "address": "Bopal, Ahmedabad, Gujarat 380058",
            "city": "Ahmedabad",
            "pincode": "380058",
            "phone": "0792345678",
            "school_board": "CBSE",
            "principal": "Dr. Sharma",
            "rating": 4.6,
            "entity_type": "school"
        }
        append_record_to_csv(temp_csv, rec, "school", ["School Board", "Principal"])

        # Read back
        with open(temp_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["School Name"] == "Delhi Public School"
            assert rows[0]["School Board"] == "CBSE"
            assert rows[0]["Principal"] == "Dr. Sharma"
        print("  [PASS] Immediate disk CSV writing with custom fields verified")
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

def test_duplicate_detector():
    print("\n=== Testing Duplicate Detector Across Pincodes ===")
    detector = DuplicateDetector()
    rec1 = {
        "name": "Apollo International School",
        "phone": "07923287000",
        "address": "Gandhinagar Ahmedabad",
        "source_url": "https://maps.google.com/place1"
    }
    detector.register(rec1)

    rec2 = {
        "name": "apollo international school",
        "phone": "+91 79 2328 7000",
        "address": "Gandhinagar Ahmedabad",
        "source_url": "https://maps.google.com/place1"
    }
    assert detector.is_duplicate(rec2) == True
    print("  [PASS] Cross-pincode duplicate normalized matching verified")

from scraper.record_normalizer import (
    is_valid_category_name,
    validate_and_normalize_pincode,
    validate_and_normalize_phone,
    clean_address_string,
    extract_area_from_address,
    parse_hours,
    normalize_business_record
)
from scraper.bs4_parser import extract_review_count, extract_rating, extract_phone, extract_pincode

def test_normalization_and_field_purity():
    print("\n=== Testing Data Extraction & Normalization Pipeline ===")

    # 1. Category validation: NEVER accept review counts, ratings, or timings
    assert not is_valid_category_name("(14)")
    assert not is_valid_category_name("(111)")
    assert not is_valid_category_name("(255)")
    assert not is_valid_category_name("(1,907)")
    assert not is_valid_category_name("14")
    assert not is_valid_category_name("4.9")
    assert not is_valid_category_name("Open · Closes 8 pm")
    assert not is_valid_category_name("Open 24 hours")
    assert is_valid_category_name("Coaching Center")
    assert is_valid_category_name("School")
    assert is_valid_category_name("Restaurant")
    assert is_valid_category_name("Solar Energy Company")
    print("  [PASS] Category validation rejects review counts and timings")

    # 2. Review count extraction: integer conversion
    assert extract_review_count("(14)") == 14
    assert extract_review_count("(1,907)") == 1907
    assert extract_review_count("1.2k reviews") == 1200
    assert extract_review_count("27 reviews") == 27
    assert extract_review_count("(111)") == 111
    print("  [PASS] Review count extracts integer from (14), (1,907), 1.2k, (111)")

    # 3. Address cleaning: NEVER contains timing or phone numbers
    dirty_addr1 = "Open, · Closes 8:30 pm, , ·, , 081559 61393"
    assert clean_address_string(dirty_addr1, phone="081559 61393") == ""
    
    clean_addr = clean_address_string("150 Feet Ring Road, Raiya Road, Rajkot, Gujarat 360007 · Open · Closes 8 pm · 098982 26848", phone="098982 26848")
    assert "Open" not in clean_addr
    assert "Closes" not in clean_addr
    assert "150 Feet Ring Road" in clean_addr
    print("  [PASS] Address cleaning strips timing and contact numbers")

    # 4. Pincode validation: NEVER 5-digit phone fragments
    assert validate_and_normalize_pincode("61303", country="India") == ""
    assert validate_and_normalize_pincode("26955", country="India") == ""
    assert validate_and_normalize_pincode("91929", country="India") == ""
    assert validate_and_normalize_pincode("360001", country="India") == "360001"
    assert validate_and_normalize_pincode("380015", country="India") == "380015"
    assert validate_and_normalize_pincode("SW1A 1AA", country="UK") == "SW1A 1AA"
    print("  [PASS] Pincode strictly validates 6 digits for India and rejects truncated numbers")

    # 5. Phone normalization: Never combined with pincode
    assert validate_and_normalize_phone("094287 61303") == "9428761303"
    assert validate_and_normalize_phone("+91 98982 26848") == "9898226848"
    assert validate_and_normalize_phone("0281 2456789") == "0281 2456789"
    assert validate_and_normalize_phone("") == ""
    print("  [PASS] Phone normalization verified")

    # 6. Timing parser
    op, cl, full = parse_hours("Open 24 hours")
    assert op == "12:00 AM" and cl == "11:59 PM" and full == "Open 24 hours"

    op, cl, full = parse_hours("Open · Closes 10 pm")
    assert op == "" and cl == "10:00 PM" and "Closes 10:00 PM" in full

    op, cl, full = parse_hours("Closed · Opens 6:30 pm")
    assert op == "6:30 PM" and cl == "" and "Opens 6:30 PM" in full

    op, cl, full = parse_hours("9:00 AM – 8:00 PM")
    assert op == "9:00 AM" and cl == "8:00 PM" and full == "9:00 AM – 8:00 PM"
    print("  [PASS] Hours parser splits opening_time, closing_time, and full_timing")

    # 7. Complete Canonical Record Normalization
    raw_sample = {
        "name": "LK Academy Rajkot",
        "category": "Coaching Center",
        "address": "2nd Floor, Dwarika Complex, 150 Feet Ring Rd, Rajkot, Gujarat 360004",
        "phone": "081559 61393",
        "rating": "4.8",
        "review_count": "(111)",
        "timing_str": "Open · Closes 8:30 pm",
        "source_url": "https://www.google.com/maps/place/LK+Academy"
    }
    norm = normalize_business_record(raw_sample, query_context={"city": "Rajkot", "country": "India", "pincode": "360004"})
    assert norm["name"] == "LK Academy Rajkot"
    assert norm["category"] == "Coaching Center"
    assert norm["google_rating"] == 4.8
    assert norm["total_reviews"] == 111
    assert "Open" not in norm["address"]
    assert norm["pincode"] == "360004"
    assert norm["phone_number"] == "8155961393"
    assert norm["closing_time"] == "8:30 PM"
    assert norm["google_maps_url"] == "https://www.google.com/maps/place/LK+Academy"
    print("  [PASS] Canonical record normalization conforms 100% to schema")

def main():
    test_dynamic_nlp_parser()
    test_dynamic_csv_and_custom_fields()
    test_duplicate_detector()
    test_normalization_and_field_purity()
    print("\n>>> ALL AUTOMATED TESTS PASSED SUCCESSFULLY <<<")

if __name__ == "__main__":
    main()
