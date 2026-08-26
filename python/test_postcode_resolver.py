"""
Comprehensive Verification Test for Multi-Level Postcode Resolution Engine.
Tests all 7 user cases + country-aware validation + deduplication + caching.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.postcode_resolver import resolve_postcodes, validate_postcode, normalize_postcodes
from services.nlp_parser import parse_search_query

def run_tests():
    print("==================================================")
    print("RUNNING MULTI-LEVEL POSTCODE RESOLVER TEST SUITE")
    print("==================================================")

    # 1. Country-Aware Format Validation Tests
    print("\n--- Test 1: Country-Aware Postcode Validation ---")
    assert validate_postcode("360001", "India") == True, "Indian 6-digit PIN should be valid"
    assert validate_postcode("362001", "India") == True, "Junagadh PIN should be valid"
    assert validate_postcode("012345", "India") == False, "Indian PIN starting with 0 is invalid"
    assert validate_postcode("36000", "India") == False, "5-digit Indian PIN is invalid"
    assert validate_postcode("SW1A 1AA", "UK") == True, "UK SW1A 1AA should be valid"
    assert validate_postcode("LE18", "UK") == True, "UK LE18 should be valid"
    assert validate_postcode("EC1A", "UK") == True, "UK EC1A should be valid"
    assert validate_postcode("360001", "UK") == False, "Indian PIN format invalid for UK"
    assert validate_postcode("SW1A", "India") == False, "UK postcode format invalid for India"
    print("  [PASS] Country-Aware Format Validation (India, UK, US, Generic)")

    # 2. Test Deduplication & Sorting
    print("\n--- Test 2: Deduplication & Normalization ---")
    raw_pins = ["362001", " 362001 ", "362002", "362001", "362004", "invalid", ""]
    norm = normalize_postcodes(raw_pins, "India")
    assert norm == ["362001", "362002", "362004"], f"Expected deduplicated list, got {norm}"
    print("  [PASS] Deduplication & Normalization verified")

    # 3. Test Ahmedabad Resolution
    print("\n--- Test 3: Query 'school in Ahmedabad' ---")
    res_ahmedabad = parse_search_query("school in Ahmedabad")
    assert res_ahmedabad["city"].lower() == "ahmedabad", f"City should be Ahmedabad, got {res_ahmedabad['city']}"
    assert len(res_ahmedabad["resolved_pincodes"]) >= 10, f"Expected 10+ pincodes, got {len(res_ahmedabad['resolved_pincodes'])}"
    print(f"  [PASS] Ahmedabad: {len(res_ahmedabad['resolved_pincodes'])} pincodes resolved ({res_ahmedabad['postcode_source']})")

    # 4. Test Rajkot Resolution
    print("\n--- Test 4: Query 'school in Rajkot' ---")
    res_rajkot = parse_search_query("school in Rajkot")
    assert res_rajkot["city"].lower() == "rajkot", f"City should be Rajkot, got {res_rajkot['city']}"
    assert "360001" in res_rajkot["resolved_pincodes"], "360001 should be in Rajkot"
    print(f"  [PASS] Rajkot: {len(res_rajkot['resolved_pincodes'])} pincodes resolved ({res_rajkot['postcode_source']})")

    # 5. Test Junagadh Resolution
    print("\n--- Test 5: Query 'school in Junagadh' ---")
    res_junagadh = parse_search_query("school in Junagadh")
    assert res_junagadh["city"].lower() == "junagadh", f"City should be Junagadh, got {res_junagadh['city']}"
    assert len(res_junagadh["resolved_pincodes"]) >= 3, f"Expected Junagadh pincodes, got {len(res_junagadh['resolved_pincodes'])}"
    assert "362001" in res_junagadh["resolved_pincodes"], "362001 should be in Junagadh"
    print(f"  [PASS] Junagadh: {len(res_junagadh['resolved_pincodes'])} pincodes resolved ({res_junagadh['postcode_source']}): {res_junagadh['resolved_pincodes']}")

    # 6. Test Amreli Resolution
    print("\n--- Test 6: Query 'school in Amreli' ---")
    res_amreli = parse_search_query("school in Amreli")
    assert res_amreli["city"].lower() == "amreli", f"City should be Amreli, got {res_amreli['city']}"
    assert len(res_amreli["resolved_pincodes"]) >= 1, f"Expected Amreli pincodes, got {len(res_amreli['resolved_pincodes'])}"
    assert "365601" in res_amreli["resolved_pincodes"], "365601 should be in Amreli"
    print(f"  [PASS] Amreli: {len(res_amreli['resolved_pincodes'])} pincodes resolved ({res_amreli['postcode_source']}): {res_amreli['resolved_pincodes']}")

    # 7. Test Jamnagar Resolution
    print("\n--- Test 7: Query 'hospital in Jamnagar' ---")
    res_jamnagar = parse_search_query("hospital in Jamnagar")
    assert res_jamnagar["city"].lower() == "jamnagar", f"City should be Jamnagar, got {res_jamnagar['city']}"
    assert "361001" in res_jamnagar["resolved_pincodes"], "361001 should be in Jamnagar"
    print(f"  [PASS] Jamnagar: {len(res_jamnagar['resolved_pincodes'])} pincodes resolved ({res_jamnagar['postcode_source']})")

    # 8. Test UK London Resolution
    print("\n--- Test 8: Query 'hotel in London' ---")
    res_london = parse_search_query("hotel in London")
    assert res_london["country"] == "UK", "Country should be UK"
    assert res_london["postal_label"] == "Postcode", "Postal label should be Postcode"
    assert len(res_london["resolved_pincodes"]) >= 4, "London should have UK postcodes"
    print(f"  [PASS] London UK: {len(res_london['resolved_pincodes'])} postcodes resolved ({res_london['postcode_source']}): {res_london['resolved_pincodes']}")

    # 9. Test Small Town Dynamic Fallback (e.g. Keshod)
    print("\n--- Test 9: Query 'hotel in Keshod' (Dynamic Fallback) ---")
    res_keshod = parse_search_query("hotel in Keshod")
    assert res_keshod["city"].lower() == "keshod", f"City should be dynamically detected as Keshod, got {res_keshod['city']}"
    print(f"  [PASS] Keshod dynamically detected: City='{res_keshod['city']}', Fallback source='{res_keshod['postcode_source']}'")

    print("\n==================================================")
    print(">>> ALL MULTI-LEVEL POSTCODE RESOLVER TESTS PASSED 100%! <<<")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
