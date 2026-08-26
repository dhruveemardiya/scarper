"""
In-Memory Duplicate Detector:
Maintains in-memory normalized hashes to prevent duplicate records across multiple scraping runs or sources.
Priority:
1. Google Maps Place URL / Place ID
2. Normalized Business Name + Normalized Address
3. Normalized Business Name + Normalized Phone
"""

import re
import hashlib
from typing import Set, Dict, Any, Optional, List, Tuple

def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    # Lowercase, remove special characters, collapse whitespace
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    return " ".join(t.split())

def normalize_phone(phone: Optional[str]) -> str:
    if not phone:
        return ""
    # Keep only digits, strip leading 0 or +91 / 91
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) > 10:
        digits = digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits

def extract_place_id_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    # Look for place identifier pattern like !1s0x...:0x... or /maps/place/<name>/
    match = re.search(r"!1s(0x[0-9a-fA-F]+:[0-9a-fA-F]+)", url)
    if match:
        return match.group(1).lower()
    place_match = re.search(r"/maps/place/([^/@?]+)", url)
    if place_match:
        return place_match.group(1).lower().strip()
    return None

class DuplicateDetector:
    def __init__(self):
        self.seen_hashes: Set[str] = set()

    def generate_candidate_keys(self, record: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Generates candidate (key_type, raw_key) tuples for robust matching.
        """
        source_url = record.get("source_url") or record.get("Google Maps URL") or ""
        place_id = extract_place_id_from_url(source_url)
        name = normalize_text(record.get("name") or record.get("Business Name") or record.get("Institute Name") or record.get("Hospital Name") or record.get("Restaurant Name") or "")
        phone = normalize_phone(record.get("phone") or record.get("Phone Number") or "")
        address = normalize_text(record.get("address") or record.get("Full Address") or "")
        city = normalize_text(record.get("city") or record.get("City") or "")

        candidates = []
        if place_id:
            candidates.append(("Place ID", f"PLACE:{place_id}"))

        # Core name: remove city suffix or hyphens (e.g. 'Aastha Hospital - Amreli' -> 'aastha hospital')
        core_name = name
        if city and city in core_name:
            core_name = normalize_text(core_name.replace(city, ""))
        if " - " in (record.get("name") or ""):
            core_name = normalize_text((record.get("name") or "").split(" - ")[0])

        # Ignore generic placeholder names from name-based dedup
        if name in ["results", "search results", "all results", "explore results", "business", "record", "unnamed"]:
            name = ""
            core_name = ""

        if name and address and len(address) >= 6:
            candidates.append(("Name + Address", f"NAME_ADDR:{name}|{address[:40]}"))
        if core_name and core_name != name and address and len(address) >= 6:
            candidates.append(("Name + Address", f"NAME_ADDR:{core_name}|{address[:40]}"))

        if name and phone and len(phone) >= 7:
            candidates.append(("Name + Phone", f"NAME_PHONE:{name}|{phone}"))
        if core_name and core_name != name and phone and len(phone) >= 7:
            candidates.append(("Name + Phone", f"NAME_PHONE:{core_name}|{phone}"))

        if phone and len(phone) >= 10:
            candidates.append(("Phone Number", f"PHONE:{phone}"))

        if name and city and len(name) >= 3:
            candidates.append(("Name + City", f"NAME_CITY:{name}|{city}"))
        if core_name and core_name != name and city and len(core_name) >= 3:
            candidates.append(("Name + City", f"NAME_CITY:{core_name}|{city}"))

        if name and len(name) >= 4:
            candidates.append(("Name", f"NAME:{name}"))
        elif source_url:
            candidates.append(("URL", f"RAW:{source_url}"))

        return candidates

    def generate_hash(self, record: Dict[str, Any]) -> str:
        candidates = self.generate_candidate_keys(record)
        if candidates:
            _, primary_key = candidates[0]
            return hashlib.md5(primary_key.encode("utf-8")).hexdigest()
        return hashlib.md5(b"EMPTY").hexdigest()

    def is_duplicate(self, record: Dict[str, Any]) -> bool:
        candidates = self.generate_candidate_keys(record)
        for _, key in candidates:
            h = hashlib.md5(key.encode("utf-8")).hexdigest()
            if h in self.seen_hashes:
                return True
        return False

    def get_duplicate_reason(self, record: Dict[str, Any]) -> str:
        candidates = self.generate_candidate_keys(record)
        for key_type, key in candidates:
            h = hashlib.md5(key.encode("utf-8")).hexdigest()
            if h in self.seen_hashes:
                return f"Matched {key_type} already saved in dataset"
        return "Duplicate record already saved"

    def register(self, record: Dict[str, Any]) -> str:
        candidates = self.generate_candidate_keys(record)
        primary_hash = ""
        for idx, (_, key) in enumerate(candidates):
            h = hashlib.md5(key.encode("utf-8")).hexdigest()
            self.seen_hashes.add(h)
            if idx == 0:
                primary_hash = h
        if not primary_hash:
            primary_hash = hashlib.md5(b"EMPTY").hexdigest()
            self.seen_hashes.add(primary_hash)
        record["duplicate_hash"] = primary_hash
        return primary_hash

    def reset(self):
        self.seen_hashes.clear()

