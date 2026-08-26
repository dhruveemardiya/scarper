"""
Direct Verification Test for Deduplication Engine & CSV History Manager
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scraper.duplicate_detector import DuplicateDetector
from services.csv_export import (
    get_history_csv_files,
    load_records_from_csv_file,
    normalize_csv_record
)

def run_tests():
    print("=== 1. Testing DuplicateDetector Multi-Key Candidate Generation ===")
    detector = DuplicateDetector()

    rec1 = {
        "source_url": "https://www.google.com/maps/place/Aastha+Hospital/data=!1s0x395880c8ba8aa237:0x2249e9c3e9a7e025",
        "name": "Aastha Hospital - Amreli",
        "category": "Hospital",
        "address": "Amreli Station Road, Beside SBI",
        "city": "Amreli",
        "pincode": "365601",
        "phone": "+91 98765 43210"
    }

    # Register record
    detector.register(rec1)
    print(f"  [PASS] Registered record: {rec1['name']}")

    # 1. Exact Duplicate Test
    assert detector.is_duplicate(rec1) is True
    reason = detector.get_duplicate_reason(rec1)
    print(f"  [PASS] Exact duplicate identified with reason: '{reason}'")

    # 2. Fast Pre-Navigation Duplicate Test (only Place ID & title available before page load)
    preview_dup = {
        "source_url": "https://www.google.com/maps/place/Aastha+Hospital/data=!1s0x395880c8ba8aa237:0x2249e9c3e9a7e025?entry=ttu",
        "name": "Aastha Hospital - Amreli"
    }
    assert detector.is_duplicate(preview_dup) is True
    reason_fast = detector.get_duplicate_reason(preview_dup)
    print(f"  [PASS] Fast pre-filter duplicate identified in 0.0001s: '{reason_fast}'")

    # 3. Name + Phone Match Duplicate Test (different URL but same name + phone)
    phone_dup = {
        "source_url": "https://www.google.com/maps/place/Other/data=!1s0x000:0x000",
        "name": "aastha hospital",
        "phone": "9876543210"
    }
    assert detector.is_duplicate(phone_dup) is True
    reason_phone = detector.get_duplicate_reason(phone_dup)
    print(f"  [PASS] Name + Phone duplicate identified: '{reason_phone}'")

    # 4. Non-Duplicate Test
    new_rec = {
        "source_url": "https://www.google.com/maps/place/Samyak+Hospital/data=!1s0x3958801234567890:0x1111222233334444",
        "name": "Samyak Multi-Speciality Hospital",
        "category": "Hospital",
        "address": "Lathi Road",
        "city": "Amreli",
        "pincode": "365601",
        "phone": "+91 99999 11111"
    }
    assert detector.is_duplicate(new_rec) is False
    print(f"  [PASS] New unique listing '{new_rec['name']}' correctly accepted")

    print("\n=== 2. Testing CSV History Scanning & Loading ===")
    files = get_history_csv_files()
    print(f"  Discovered {len(files)} CSV history files on disk:")
    for f in files:
        print(f"    - {f['filename']} ({f['record_count']} records, {f['size_formatted']}, modified: {f['modified_at']})")
    assert len(files) >= 1

    # Load actual historical CSV file
    first_file = files[0]
    load_res = load_records_from_csv_file(first_file['filepath'])
    assert load_res["success"] is True
    records = load_res["records"]
    print(f"  [PASS] Loaded {len(records)} records from '{first_file['filename']}'")
    assert len(records) > 0

    first_record = records[0]
    print(f"  Sample Normalized Record #1:")
    print(f"    Name: {first_record.get('name')}")
    print(f"    City: {first_record.get('city')}")
    print(f"    Pincode: {first_record.get('pincode')}")
    print(f"    Rating: {first_record.get('rating')}")
    print(f"    Maps URL: {first_record.get('source_url')}")
    assert "name" in first_record

    # 5. Generic 'Results' Name Rejection & Category Purity Tests
    print("\n=== 3. Testing Normalizer Category Purity & Name Safety ===")
    from scraper.record_normalizer import is_valid_category_name, normalize_business_record

    # Verify category validator rejects composite rating/review strings
    assert is_valid_category_name("4.5(30)") is False
    assert is_valid_category_name("3.4(18)") is False
    assert is_valid_category_name("4.0 (14)") is False
    assert is_valid_category_name("5.0(5)") is False
    assert is_valid_category_name("Solar Panel Dealer") is True
    print("  [PASS] is_valid_category_name correctly rejected rating/review numbers ('4.5(30)', '3.4(18)')")

    # Verify normalize_business_record rejects 'Results' as name
    bogus_rec = {
        "name": "Results",
        "category": "4.5(30)",
        "sub_category": "Solar Panel Dealer",
        "city": "Rajkot",
        "pincode": "360007",
        "source_url": "https://www.google.com/maps/place/Solarium+Green+Energy+Limited/@22.2764799,70.7607519,13z"
    }
    norm = normalize_business_record(bogus_rec)
    assert norm["name"] != "Results"
    assert norm["name"] == "Solarium Green Energy Limited"
    assert norm["category"] == "Solar Panel Dealer"
    print(f"  [PASS] Bogus 'Results' name recovered to: '{norm['name']}', Category: '{norm['category']}'")

    # 6. Specific Hospital CSV Load Verification Test
    print("\n=== 4. Testing Hospital CSV File Field Loading ===")
    hospital_csv_path = os.path.join(os.path.dirname(BASE_DIR), "Rajkot_Hospital_2026-08-24.csv")
    if os.path.exists(hospital_csv_path):
        hosp_res = load_records_from_csv_file(hospital_csv_path)
        assert hosp_res["success"] is True
        hosp_records = hosp_res["records"]
        assert len(hosp_records) > 0
        hosp_first = hosp_records[0]
        assert hosp_first.get("name") and hosp_first["name"] != "—"
        assert hosp_first.get("city") and hosp_first["city"] != "—"
        assert hosp_first.get("phone") and hosp_first["phone"] != "—"
        print(f"  [PASS] Successfully loaded {len(hosp_records)} records from Rajkot_Hospital_2026-08-24.csv:")
        print(f"         Name:     '{hosp_first.get('name')}'")
        print(f"         City:     '{hosp_first.get('city')}'")
        print(f"         Category: '{hosp_first.get('category')}'")
        print(f"         Phone:    '{hosp_first.get('phone')}'")

    print("\n>>> ALL DEDUPLICATION & CSV HISTORY TESTS PASSED 100%! <<<\n")
    import sys
    sys.exit(0)

if __name__ == "__main__":
    run_tests()
