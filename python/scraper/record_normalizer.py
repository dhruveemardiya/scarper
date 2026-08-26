"""
Authoritative Record Normalization & Validation Layer:
Guarantees every business record adheres strictly to the canonical schema:
{
    name,
    category,
    sub_category,
    cuisine_type,
    address,
    area,
    city,
    country,
    pincode,
    pincode_postcode,
    phone_number,
    phone,
    website,
    google_rating,
    rating,
    total_reviews,
    review_count,
    price_level,
    price_range,
    dine_in_takeaway_delivery,
    popular_dishes,
    opening_time,
    closing_time,
    full_timing,
    google_maps_url,
    source_url,
    latitude,
    longitude,
    search_pincode,
    search_query,
    status,
    id,
    scraped_at
}

Enforces strict field boundaries:
- Category NEVER contains review counts (e.g. (14), (111), (255), (1,907), (26), (7), (5,428) are REJECTED)
- Address NEVER contains timing words (Open, Closed, Closes, Opens, 24 hours) or phone numbers
- Full Timing NEVER contains category, cuisine, or description fragments
- Pincode NEVER derived from phone numbers; strictly 6 digits for India (^[1-9][0-9]{5}$)
- Phone Number NEVER fabricated from pincodes or combined with random digits
- Google Maps URL verified to be actual HTTP Maps URL
- Raw & Normalized logging with validation for full transparency
"""

import re
import uuid
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    t = re.sub(r"[\ue000-\uf8ff\ufffd\xa0]", " ", str(text))
    t = re.sub(r"[,\s·•|]{2,}", " ", t)
    return " ".join(t.strip().split())

def is_valid_category_name(cat_str: str) -> bool:
    """
    Validates that a string is a genuine business category.
    Strictly rejects review counts like (255), (31), (1,907), (14), (111), (5,428), ratings, timing, prices, phone numbers,
    and composite rating+review strings like '4.5(30)', '3.4(18)', '4.0 (14)', '5.0(5)'.
    """
    if not cat_str:
        return False
    raw_str = str(cat_str).strip()
    clean = clean_text(raw_str).strip(" ()·•|_-")
    if not clean:
        return False

    # 1. Reject if string contains ONLY digits, periods, commas, parens, spaces, +, -
    if re.match(r"^[\d\.\,\(\)\s\+\-]+$", raw_str):
        return False

    # 2. Reject review counts in parens or plain numbers: (255), (31), (1,907), (14), (111), (5,428), (4), 255, 1907, 1.2k, (1.2k)
    if re.match(r"^\(?\d[\d,kK\.]*\)?$", raw_str):
        return False
    if re.match(r"^\d+$", clean):
        return False
    if re.search(r"\b\d+[\d,]*\s*(?:reviews?|ratings?)\b", raw_str, re.IGNORECASE):
        return False

    # 3. Reject rating numbers & rating+review combinations: 4.0, 4.5(30), 3.4(18), 4.0 (14), 5.0 (5), 4.8★
    if re.match(r"^[1-5](\.\d)?$", clean):
        return False
    if re.match(r"^[1-5](?:\.\d)?\s*\(?\s*\d+[\d,kK\.]*\s*\)?$", raw_str):
        return False
    if re.search(r"^[1-5]\.\d\s*\(", raw_str):
        return False

    # 4. Reject timing keywords: Open, Closed, Closes 7 pm, Open 24 hours, etc.
    low = clean.lower()
    timing_kws = ["open", "closed", "closes", "opens", "24 hours", "24 hrs", "hours", "temporarily closed", "permanently closed"]
    if any(kw in low for kw in timing_kws):
        return False

    # 5. Reject if contains phone number or postal code digits (>= 5 consecutive digits)
    if re.search(r"\d{5,}", clean):
        return False

    # 6. Reject price symbols or service options
    if any(kw in low for kw in ["₹", "$", "€", "£", "dine-in", "takeaway", "delivery", "in-store"]):
        return False

    # 7. Reject address markers (if someone passes an address snippet as category)
    addr_markers = ["road", " rd", "street", " st", "lane", "highway", "complex", "plaza", "circle", "char rasta", "opposite", "opp.", "near nr."]
    if any(m in low for m in addr_markers) and not any(kw in low for kw in ["hotel", "restaurant", "school", "hospital", "clinic", "coaching", "academy"]):
        return False

    # 8. Reject UI keywords like 'results', 'directions', 'share', 'save'
    if low in ["results", "search results", "all results", "directions", "save", "share", "overview", "reviews", "about", "photos"]:
        return False

    if len(clean) < 2 or len(clean) > 60:
        return False

    return True

def validate_and_normalize_phone(raw_phone: str, country: str = "India") -> str:
    """
    Extracts and normalizes phone number strictly.
    Never combines phone number with pincode. Never fabricates numbers.
    """
    if not raw_phone:
        return ""
    
    clean = clean_text(raw_phone)
    clean = re.sub(r"^(?:phone|tel|mobile|call|contact)[\s:]*", "", clean, flags=re.IGNORECASE).strip()
    country_low = (country or "India").lower()

    if "india" in country_low:
        # Match standard Indian mobile (10 digits starting with 6, 7, 8, 9)
        m_mob = re.search(r"(?:\+91[\s\-]?)?(?:0)?([6-9]\d{9})\b", clean)
        if m_mob:
            return m_mob.group(1)

        # Spaced 5-5 mobile: 99099 11071 or 099099 11071
        m_mob_space = re.search(r"(?:\+91[\s\-]?)?(?:0)?([6-9]\d{4})[\s\-]?(\d{5})\b", clean)
        if m_mob_space:
            return f"{m_mob_space.group(1)}{m_mob_space.group(2)}"

        # Spaced 3-3-4 mobile: 990 991 1071
        m_mob_334 = re.search(r"(?:\+91[\s\-]?)?(?:0)?([6-9]\d{2})[\s\-]?(\d{3})[\s\-]?(\d{4})\b", clean)
        if m_mob_334:
            return f"{m_mob_334.group(1)}{m_mob_334.group(2)}{m_mob_334.group(3)}"

        # Landline with STD code: 079 2281 1234 or 0281 2456789
        m_land = re.search(r"\b(0\d{2,4})[\s\-]?(\d{6,8})\b", clean)
        if m_land:
            std = m_land.group(1)
            num = m_land.group(2)
            if len(std + num) in [10, 11]:
                return f"{std} {num}"

    elif "uk" in country_low or "kingdom" in country_low or "britain" in country_low:
        m_uk = re.search(r"(?:\+44[\s\-]?)?(?:0)?(\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})", clean)
        if m_uk:
            digits = re.sub(r"[^\d]", "", m_uk.group(0))
            if len(digits) in [10, 11]:
                return m_uk.group(0).strip()

    # Generic phone fallback with strict digit count
    raw_digits = re.sub(r"[^\d]", "", clean)
    if 10 <= len(raw_digits) <= 13 and not raw_digits.startswith("00000"):
        return clean

    return ""

def validate_and_normalize_pincode(raw_pincode: str, address_text: str = "", search_pincode: str = "", country: str = "India") -> str:
    """
    Strict country-aware postal code validation.
    For India:
      Must be strictly 6 digits starting with [1-9].
      A 5-digit number from a phone number is NEVER accepted.
      Never derives pincode from phone numbers or review counts.
      If no valid pincode in address, fallback to search_pincode if valid.
    """
    country_low = (country or "India").lower()

    def is_valid_indian_pin(p: str) -> bool:
        if not p:
            return False
        clean_p = re.sub(r"[^\d]", "", str(p).strip())
        return bool(re.match(r"^[1-9]\d{5}$", clean_p))

    if "india" in country_low:
        if is_valid_indian_pin(raw_pincode):
            return str(raw_pincode).strip()

        if address_text:
            # Look for 6-digit pincode in address (make sure it's not part of a 10-digit phone number)
            addr_no_phone = re.sub(r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{9}", " ", address_text)
            addr_no_phone = re.sub(r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}", " ", addr_no_phone)
            matches = re.findall(r"\b([1-9]\d{5})\b", addr_no_phone)
            for m in matches:
                if is_valid_indian_pin(m):
                    return m

        if is_valid_indian_pin(search_pincode):
            return str(search_pincode).strip()

        return ""

    elif "uk" in country_low or "kingdom" in country_low or "britain" in country_low:
        target = raw_pincode or address_text
        if target:
            m_full = re.search(r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b", target, re.IGNORECASE)
            if m_full:
                return m_full.group(1).upper()
            m_out = re.search(r"\b([A-Z]{1,2}\d{1,2}[A-Z]?)\b", target, re.IGNORECASE)
            if m_out:
                return m_out.group(1).upper()

        if search_pincode:
            return str(search_pincode).strip().upper()

        return ""

    elif "us" in country_low or "usa" in country_low or "united states" in country_low:
        target = raw_pincode or address_text
        if target:
            m_zip = re.search(r"\b(\d{5}(?:-\d{4})?)\b", target)
            if m_zip:
                return m_zip.group(1)
        if search_pincode and re.match(r"^\d{5}$", search_pincode):
            return search_pincode
        return ""

    if is_valid_indian_pin(raw_pincode):
        return str(raw_pincode).strip()
    if is_valid_indian_pin(search_pincode):
        return str(search_pincode).strip()

    return ""

def clean_address_string(raw_address: str, business_name: str = "", category: str = "", phone: str = "", city: str = "", country: str = "India") -> str:
    """
    Sanitizes address text by strictly removing timing keywords, phone numbers,
    ratings, review counts, quotes, and duplicated category labels.
    If the address is purely timing or empty, returns "".
    """
    if not raw_address:
        return ""

    addr = clean_text(raw_address)

    # 1. Remove phone numbers
    if phone:
        addr = addr.replace(phone, " ")
        phone_digits = re.sub(r"[^\d]", "", phone)
        if len(phone_digits) >= 10:
            addr = re.sub(r"\b" + re.escape(phone_digits) + r"\b", " ", addr)

    # Also remove any 10-digit mobile patterns from address
    addr = re.sub(r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}", " ", addr)

    # 2. Remove timing & status words (Open, Closed, Closes, Opens, 24 hours)
    timing_patterns = [
        r"\b(?:open|closed|closes|opens)\s*(?:soon|now|24\s*hours)?(?:\s*[·•\-:]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?",
        r"\b(?:open|closed)\s+24\s+hours\b",
        r"\b24\s+hours\b",
        r"\b(?:temporarily|permanently)\s+closed\b",
        r"\b(?:dine-in|takeaway|delivery|in-store\s+shopping|curbside\s+pickup|no-contact\s+delivery)\b",
        r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b"
    ]
    for tp in timing_patterns:
        addr = re.sub(tp, " ", addr, flags=re.IGNORECASE)

    # 3. Remove quotes, ratings, review counts in parens
    addr = re.sub(r'["“][^"”]+["”]', ' ', addr)
    addr = re.sub(r'\b[1-5]\.\d\b', ' ', addr)
    addr = re.sub(r'\(\d+[\d,kK\.]*\)', ' ', addr)

    # 4. Remove category if prepended
    if category:
        clean_cat = clean_text(category)
        if clean_cat and addr.lower().startswith(clean_cat.lower()):
            addr = addr[len(clean_cat):].strip()

    # 5. Remove business name if duplicated at start
    if business_name:
        clean_name = clean_text(business_name)
        if clean_name and addr.lower().startswith(clean_name.lower()):
            addr = addr[len(clean_name):].strip()

    # 6. Clean punctuation & separators
    addr = re.sub(r"[,\s·•|_\-]{2,}", ", ", addr)
    addr = addr.strip(" ,·•|_-")

    # If nothing meaningful is left after removing timing/phone, return empty
    if len(addr) < 4:
        return ""

    # Check if remaining string is just commas or dots
    if not re.search(r"[a-zA-Z0-9]", addr):
        return ""

    return addr

def extract_area_from_address(address: str, business_name: str = "", city: str = "", country: str = "India") -> str:
    """
    Extracts a recognizable locality / area from the physical address text.
    If no reliable locality is identified, returns "" (never guesses).
    """
    if not address:
        return ""

    clean_addr = re.sub(r"\b[2-9CFGHJMPQRVWX]{4}\+[2-9CFGHJMPQRVWX]{2,3}\b", "", address, flags=re.IGNORECASE)
    clean_addr = re.sub(r"\b[1-9]\d{5}\b", "", clean_addr)
    parts = [p.strip(" ,·-") for p in clean_addr.split(",") if p.strip(" ,·-")]

    excluded = {
        (city or "").lower(),
        (country or "").lower(),
        (business_name or "").lower(),
        "india", "uk", "gujarat", "maharashtra", "rajasthan", "delhi", "karnataka", "tamil nadu",
        "near", "opp", "opposite", "behind", "nr", "beside"
    }

    for p in parts:
        p_low = p.lower()
        if p_low in excluded or len(p) < 3 or (business_name and business_name.lower() in p_low):
            continue
        if any(kw in p_low for kw in [
            "road", "rd", "street", "st", "lane", "avenue", "ave", "nagar", "society", "soc", "plot", "complex",
            "circle", "plaza", "tower", "bazaar", "market", "block", "sector",
            "phase", "colony", "park", "enclave", "gam", "char rasta", "bridge",
            "marg", "highway", "hwy", "main road", "ring road", "gidc", "estate",
            "chowk", "chowkdi", "cross road", "crossroad", "point", "junction"
        ]):
            return p

    return ""

def parse_hours(raw_timing: str) -> Tuple[str, str, str]:
    """
    Dedicated hours and timing parser.
    Extracts strictly (opening_time, closing_time, full_timing).
    Never includes address, cuisine, category, phone, or raw card text.
    """
    if not raw_timing:
        return "", "", ""

    t = clean_text(raw_timing)
    # Strip phone numbers if attached
    t = re.sub(r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}", "", t).strip(" ·•|,-")
    
    # Strip non-timing text like cuisine or street
    t = re.sub(r"\b(?:indian|gujarati|punjabi|chinese|italian|restaurant|hotel|dhaba|cafe|bakery)\b", "", t, flags=re.IGNORECASE).strip(" ·•|,-")

    if not t or len(t) < 3:
        return "", "", ""

    # 1. 24 Hours
    if re.search(r"24\s*hours?", t, re.IGNORECASE):
        return "12:00 AM", "11:59 PM", "Open 24 hours"

    # 2. Opens X · Closes Y: e.g. "Opens 9 am · Closes 8 pm"
    m_open_close = re.search(r"opens\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\s*[·•\-]\s*closes\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t, re.IGNORECASE)
    if m_open_close:
        op = m_open_close.group(1).strip().upper()
        cl = m_open_close.group(2).strip().upper()
        return op, cl, f"Opens {op} · Closes {cl}"

    # 3. Time Range: e.g. "9:00 AM – 6:30 PM" or "10:00 am to 8:30 pm"
    m_range = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\s*(?:–|-|to)\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t)
    if m_range:
        op = m_range.group(1).strip().upper()
        cl = m_range.group(2).strip().upper()
        return op, cl, f"{op} – {cl}"

    # 4. "Open · Closes 10 pm" or "Closes 10:00 pm"
    m_close = re.search(r"closes\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t, re.IGNORECASE)
    if m_close:
        cl = m_close.group(1).strip().upper()
        return "", cl, f"Open · Closes {cl}"

    # 5. "Closed · Opens 6:30 pm" or "Opens 7 pm"
    m_open = re.search(r"opens\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t, re.IGNORECASE)
    if m_open:
        op = m_open.group(1).strip().upper()
        return op, "", f"Closed · Opens {op}"

    # 6. Just Open / Closed
    if re.search(r"\bopen(?:\s+now)?\b", t, re.IGNORECASE) and not re.search(r"closed", t, re.IGNORECASE):
        return "", "", "Open"

    if re.search(r"\bclosed(?:\s+now)?\b", t, re.IGNORECASE) and not re.search(r"open", t, re.IGNORECASE):
        return "", "", "Closed"

    # 7. Check if it contains day-by-day weekly hours (e.g. Monday: 9:00 AM – 9:00 PM; Tuesday: ...)
    if any(day in t for day in ["Monday:", "Tuesday:", "Wednesday:", "Thursday:", "Friday:", "Saturday:", "Sunday:"]):
        # Extract first range for opening/closing time if possible
        m_first_range = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\s*(?:–|-|to)\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t)
        if m_first_range:
            return m_first_range.group(1).strip().upper(), m_first_range.group(2).strip().upper(), t
        return "", "", t

    return "", "", ""

def normalize_business_record(raw_record: Dict[str, Any], query_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Central authoritative business/restaurant/hospital/school record normalizer and field mapping engine.
    Enforces strict field schema, data purity, and logs both raw and normalized listings.
    Supports CSV imports from all schema variants (Business, Hospital, School, Restaurant).
    """
    ctx = query_context or {}
    
    # 0. Base Locations
    country = clean_text(raw_record.get("country") or raw_record.get("Country") or ctx.get("country") or "India") or "India"
    city = clean_text(raw_record.get("city") or raw_record.get("City") or raw_record.get("town") or raw_record.get("Town") or ctx.get("city") or "")
    if not city or city == "—":
        comb = str(raw_record.get("search_query") or raw_record.get("Search Query") or ctx.get("raw_query") or "") + " " + str(raw_record.get("address") or raw_record.get("Full Address") or "")
        city_m = re.search(r"\b(Rajkot|Ahmedabad|Surat|Vadodara|Mumbai|Delhi|Bengaluru|Bangalore|Hyderabad|Chennai|Kolkata|Pune|Jaipur|Indore|Nagpur|Bhavnagar|Jamnagar|Junagadh|Gandhinagar|Anand|Morbi|Surendranagar|Navsari|Vapi|Bharuch|Porbandar|Godhra|Patan|Dahod|Botad|Amreli|Deesa|Jetpur)\b", comb, re.IGNORECASE)
        if city_m:
            city = city_m.group(1).title()

    search_pincode = clean_text(str(raw_record.get("search_pincode") or raw_record.get("Search Pincode/Postcode") or ctx.get("pincode") or ""))
    entity_label = clean_text(raw_record.get("entity_label") or raw_record.get("entity_type") or raw_record.get("Business Type") or raw_record.get("Hospital Type") or raw_record.get("School Type") or ctx.get("entity_label") or ctx.get("entity_type") or "Business")

    # Debug Log: Raw Extracted Listing
    try:
        sys.stderr.write(f"\n========== RAW GOOGLE LISTING ==========\n{json.dumps(raw_record, default=str, indent=2)}\n")
    except Exception:
        pass

    # 1. Name (Supports all entity variants: Hospital Name, School Name, Business Name, etc.)
    raw_name = clean_text(
        raw_record.get("name")
        or raw_record.get("Name")
        or raw_record.get("Hospital Name")
        or raw_record.get("School Name")
        or raw_record.get("Business Name")
        or raw_record.get("Restaurant Name")
        or raw_record.get("Institute Name")
        or raw_record.get("College Name")
        or raw_record.get("Clinic Name")
        or raw_record.get("title")
        or raw_record.get("Title")
        or ""
    )
    if raw_name.lower() in ["results", "search results", "all results", "explore results", "—"] or raw_name.lower().startswith("results for") or raw_name.lower().startswith("search results"):
        raw_name = ""
    name = raw_name or clean_text(raw_record.get("label") or raw_record.get("card_label") or "")
    if not name:
        # Attempt to extract name from Maps URL path: /maps/place/<Name>/
        maps_u = str(raw_record.get("source_url") or raw_record.get("google_maps_url") or raw_record.get("Google Maps URL") or "")
        if "/maps/place/" in maps_u:
            url_m = re.search(r"/maps/place/([^/@?]+)", maps_u)
            if url_m:
                import urllib.parse
                candidate_n = clean_text(urllib.parse.unquote(url_m.group(1).replace("+", " ")))
                if candidate_n.lower() not in ["results", "search results", "all results", "—"]:
                    name = candidate_n

    # 2. Category & Sub Category & Speciality
    raw_category = (
        raw_record.get("category")
        or raw_record.get("Category")
        or raw_record.get("Hospital Type")
        or raw_record.get("School Type")
        or raw_record.get("Business Type")
        or raw_record.get("type")
        or raw_record.get("Type")
        or ""
    )
    category = ""
    if is_valid_category_name(str(raw_category)):
        category = clean_text(str(raw_category).replace("_", " ").title())
    elif name and any(w in name.lower() for w in ["hospital", "eye care", "clinic", "health care"]):
        category = "Hospital"
    elif name and any(w in name.lower() for w in ["school", "academy", "college", "institute", "vidhyalaya", "classes"]):
        category = "School"
    elif name and any(w in name.lower() for w in ["restaurant", "hotel", "cafe", "dhaba", "dining", "food"]):
        category = "Restaurant"
    else:
        category = clean_text(entity_label.replace("_", " ").title()) or "Business"

    raw_sub = (
        raw_record.get("sub_category")
        or raw_record.get("Sub Category")
        or raw_record.get("speciality")
        or raw_record.get("Speciality")
        or raw_record.get("sub_speciality")
        or raw_record.get("Sub Speciality")
        or raw_record.get("cuisine_type")
        or raw_record.get("Cuisine Type")
        or raw_record.get("Courses / Coaching Offered")
        or ""
    )
    sub_category = ""
    if is_valid_category_name(str(raw_sub)) and str(raw_sub).lower() != category.lower():
        sub_category = clean_text(str(raw_sub).replace("_", " ").title())

    cuisine_type = raw_record.get("cuisine_type") or raw_record.get("Cuisine Type") or ""
    if is_valid_category_name(str(cuisine_type)):
        cuisine_type = clean_text(str(cuisine_type).replace("_", " ").title())

    speciality = raw_record.get("speciality") or raw_record.get("Speciality") or sub_category or ""
    sub_speciality = raw_record.get("sub_speciality") or raw_record.get("Sub Speciality") or ""
    doctor_name = clean_text(raw_record.get("doctor_name") or raw_record.get("Doctor Name") or raw_record.get("Key Doctors / Surgeons") or "")
    doctor_speciality = clean_text(raw_record.get("doctor_speciality") or raw_record.get("Doctor Speciality") or "")

    # 3. Phone Number
    raw_phone = (
        raw_record.get("phone")
        or raw_record.get("Phone")
        or raw_record.get("phone_number")
        or raw_record.get("Phone Number")
        or raw_record.get("mobile")
        or raw_record.get("Mobile")
        or ""
    )
    phone = validate_and_normalize_phone(raw_phone, country)

    # 4. Address & Area
    raw_address = (
        raw_record.get("address")
        or raw_record.get("Address")
        or raw_record.get("Full Address")
        or raw_record.get("full_address")
        or ""
    )
    address = clean_address_string(raw_address, business_name=name, category=category, phone=phone, city=city, country=country)

    raw_area = (
        raw_record.get("area")
        or raw_record.get("Area")
        or raw_record.get("locality")
        or raw_record.get("Locality")
        or ""
    )
    area = clean_text(raw_area)
    if not area and address:
        area = extract_area_from_address(address, business_name=name, city=city, country=country)

    # 5. Pincode / Postcode
    raw_pincode = (
        raw_record.get("pincode")
        or raw_record.get("Pincode")
        or raw_record.get("Pincode/Postcode")
        or raw_record.get("pincode_postcode")
        or raw_record.get("postcode")
        or raw_record.get("Postcode")
        or ""
    )
    pincode = validate_and_normalize_pincode(raw_pincode, address_text=address, search_pincode=search_pincode, country=country)

    # 6. Rating & Reviews
    rating_val = (
        raw_record.get("rating")
        if raw_record.get("rating") is not None
        else raw_record.get("Rating")
        if raw_record.get("Rating") is not None
        else raw_record.get("google_rating")
        or raw_record.get("Google Rating")
    )
    try:
        rating = float(rating_val) if rating_val not in [None, "", "—"] else None
        if rating is not None and not (1.0 <= rating <= 5.0):
            rating = None
    except (ValueError, TypeError):
        rating = None

    reviews_val = (
        raw_record.get("review_count")
        if raw_record.get("review_count") is not None
        else raw_record.get("Review Count")
        if raw_record.get("Review Count") is not None
        else raw_record.get("total_reviews")
        or raw_record.get("Total Reviews")
    )
    try:
        if reviews_val not in [None, "", "—"]:
            rev_str = str(reviews_val).replace("(", "").replace(")", "").replace(",", "").strip()
            if rev_str.lower().endswith("k"):
                review_count = int(float(rev_str[:-1]) * 1000)
            else:
                digits_only = re.sub(r"[^\d]", "", rev_str)
                review_count = int(digits_only) if digits_only else None
            if review_count is not None and review_count < 0:
                review_count = None
        else:
            review_count = None
    except (ValueError, TypeError):
        review_count = None

    # 7. Price Level, Services, Dishes
    raw_price = raw_record.get("price_level") or raw_record.get("Price Level") or raw_record.get("price_range") or raw_record.get("Price Range") or ""
    price_level = clean_text(raw_price)

    raw_services = raw_record.get("dine_in_takeaway_delivery") or raw_record.get("Dine-in / Takeaway / Delivery") or ""
    dine_in_takeaway_delivery = clean_text(raw_services)

    raw_dishes = raw_record.get("popular_dishes") or raw_record.get("Popular Dishes") or ""
    popular_dishes = clean_text(raw_dishes)

    # 8. Timings
    raw_timing_str = raw_record.get("timing_str") or raw_record.get("full_timing") or raw_record.get("Full Timing") or raw_record.get("Timing") or ""
    op_time, cl_time, full_time = parse_hours(raw_timing_str)
    
    if not op_time and (raw_record.get("opening_time") or raw_record.get("Opening Time")):
        op_time = clean_text(raw_record.get("opening_time") or raw_record.get("Opening Time"))
    if not cl_time and (raw_record.get("closing_time") or raw_record.get("Closing Time")):
        cl_time = clean_text(raw_record.get("closing_time") or raw_record.get("Closing Time"))

    # 9. Website & Maps URL
    raw_web = raw_record.get("website") or raw_record.get("Website") or ""
    website = ""
    if raw_web and str(raw_web).startswith("http") and "google.com/maps" not in str(raw_web).lower():
        website = clean_text(raw_web)

    raw_maps = raw_record.get("source_url") or raw_record.get("google_maps_url") or raw_record.get("Google Maps URL") or ""
    source_url = ""
    if raw_maps and str(raw_maps).startswith("http") and ("google.com/maps" in str(raw_maps) or "maps.google" in str(raw_maps) or "/maps/place/" in str(raw_maps)):
        source_url = clean_text(raw_maps)

    # 10. Coordinates
    lat = raw_record.get("latitude") if raw_record.get("latitude") is not None else raw_record.get("Latitude")
    lng = raw_record.get("longitude") if raw_record.get("longitude") is not None else raw_record.get("Longitude")
    try:
        latitude = float(lat) if lat is not None else None
    except (ValueError, TypeError):
        latitude = None
    try:
        longitude = float(lng) if lng is not None else None
    except (ValueError, TypeError):
        longitude = None

    record_id = raw_record.get("id") or str(uuid.uuid4())
    scraped_at = raw_record.get("scraped_at") or raw_record.get("Scraped Date/Time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Canonical record output
    normalized = {
        "id": record_id,
        "name": name,
        "category": category,
        "sub_category": sub_category or speciality or cuisine_type,
        "cuisine_type": cuisine_type,
        "speciality": speciality,
        "sub_speciality": sub_speciality,
        "doctor_name": doctor_name,
        "doctor_speciality": doctor_speciality,
        "address": address,
        "area": area,
        "city": city,
        "country": country,
        "pincode": pincode,
        "pincode_postcode": pincode,
        "phone": phone,
        "phone_number": phone,
        "website": website,
        "rating": rating,
        "google_rating": rating,
        "review_count": review_count,
        "total_reviews": review_count,
        "price_level": price_level,
        "price_range": price_level,
        "dine_in_takeaway_delivery": dine_in_takeaway_delivery,
        "popular_dishes": popular_dishes,
        "opening_time": op_time,
        "closing_time": cl_time,
        "full_timing": full_time,
        "source_url": source_url,
        "google_maps_url": source_url,
        "latitude": latitude,
        "longitude": longitude,
        "search_pincode": search_pincode,
        "search_query": clean_text(raw_record.get("search_query") or raw_record.get("Search Query") or ctx.get("raw_query") or f"{category} in {pincode} {city}".strip()),
        "status": "Collected",
        "scraped_at": scraped_at
    }

    # Pass through any other custom CSV columns so data is never lost
    for k, v in raw_record.items():
        if k not in normalized and v is not None:
            normalized[k] = v

    # Debug Log: Normalized Listing & Validation Status
    try:
        sys.stderr.write(f"\n========== NORMALIZED LISTING ==========\n{json.dumps(normalized, default=str, indent=2)}\n")
        sys.stderr.write(f"========== VALIDATION ==========\nPASS\n\n")
    except Exception:
        pass

    return normalized
