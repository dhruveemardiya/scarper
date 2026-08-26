"""
BS4 Parser:
Extracts structured business information from raw HTML and web elements using BeautifulSoup.
"""

import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    # Strip Private Use Area (PUA) and non-printable icon characters
    t = re.sub(r"[\ue000-\uf8ff\ufffd]", "", str(text))
    return " ".join(t.strip().split())

def extract_phone(text: str) -> str:
    if not text:
        return ""
    # Strip non-breaking spaces and HTML entities
    t = str(text).replace("\xa0", " ").replace("&nbsp;", " ")
    
    # Matches Indian 10-digit mobile, STD landlines, 0-prefixed mobile, +91 format, UK/US formats
    patterns = [
        r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}",
        r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{2}[\s\-]?\d{3}[\s\-]?\d{4}",
        r"\b0\d{2,4}[\s\-]?\d{6,8}\b",
        r"\(\d{2,4}\)[\s\-]?\d{6,8}",
        r"(?:\+44[\s\-]?)?(?:0\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})",
        r"(?:\+1[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",
        r"\b[6-9]\d{9}\b"
    ]
    for p in patterns:
        m = re.search(p, t)
        if m:
            raw = m.group(0).strip()
            digits = re.sub(r"[^\d+]", "", raw)
            # Avoid matching 6-digit pincodes (e.g. 382350) or 4-digit years (2026)
            if len(digits.replace("+", "")) >= 10 and len(digits) != 6:
                return raw
    return ""

def extract_pincode(text: str, default_country: str = "India") -> str:
    if not text:
        return ""
    country_low = (default_country or "India").lower()

    # 1. India - strictly 6 digits starting with 1-9 (e.g. 360001, 380015, 360021)
    if "india" in country_low:
        m_in = re.search(r"\b([1-9]\d{5})\b", text)
        if m_in:
            return m_in.group(1)
        return ""

    # 2. UK Full Postcode (e.g. LE18 2FA, SW1A 1AA, EC1A 1BB)
    if "uk" in country_low or "kingdom" in country_low or "britain" in country_low:
        m_uk_full = re.search(r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b", text, re.IGNORECASE)
        if m_uk_full:
            return m_uk_full.group(1).upper()
        m_uk_out = re.search(r"\b([A-Z]{1,2}\d{1,2}[A-Z]?)\b", text, re.IGNORECASE)
        if m_uk_out:
            candidate = m_uk_out.group(1).upper()
            if re.search(r"\b(LE|SW|NW|SE|NE|EC|WC|E|W|N|S|B|M|L|G|EH|BT|CF|BS|CB|OX|CM|CR|HA|TW|UB|WD|EN|IG|RM|DA|BR|SM|KT|GU|RG|SO|PO|BN|TN|ME|CT|SS|CO|IP|NR|PE|NN|MK|LU|AL|HP|SL|SN|BA|SP|BH|DT|EX|TQ|PL|TR|TA|GL|HR|WR|DY|WS|WV|ST|TF|SY|LD|SA|LL|CH|CW|SK|WA|WN|BL|OL|HD|HX|WF|LS|HG|BD|BB|FY|PR|LA|CA|DG|TD|ML|KA|PA|FK|KY|DD|AB|IV|KW|ZE|HS)\d", candidate):
                return candidate
        return ""

    # 3. US 5-digit ZIP code
    if "us" in country_low or "usa" in country_low or "united states" in country_low:
        m_zip = re.search(r"\b(\d{5}(?:-\d{4})?)\b", text)
        if m_zip:
            return m_zip.group(1)

    # 4. General fallback
    m_in = re.search(r"\b([1-9]\d{5})\b", text)
    if m_in:
        return m_in.group(1)

    return ""

def extract_rating(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"\b([1-5](?:\.\d)?)\b", text)
    if m:
        try:
            val = float(m.group(1))
            if 1.0 <= val <= 5.0:
                return val
        except ValueError:
            pass
    return None

def extract_review_count(text: str) -> Optional[int]:
    if not text:
        return None
    # E.g. (1,234) or 1.2k reviews or (159)
    m_k = re.search(r"(\d+(?:\.\d+)?)\s*k\b", text, re.IGNORECASE)
    if m_k:
        try:
            return int(float(m_k.group(1)) * 1000)
        except ValueError:
            pass
    m = re.search(r"\b(\d{1,3}(?:,\d{3})*|\d+)\s*(?:reviews?|ratings?|\))", text, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            pass
    m_plain = re.search(r"\b(\d+)\b", text)
    if m_plain:
        try:
            return int(m_plain.group(1))
        except ValueError:
            pass
    return None

def extract_timing_components(timing_text: str) -> Dict[str, str]:
    if not timing_text:
        return {"opening_time": "", "closing_time": "", "full_timing": ""}
    
    t = clean_text(timing_text)
    # Remove phone number or other non-timing attachments
    t = re.sub(r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}", "", t).strip(" ·•|,-")
    if not t or len(t) < 3:
        return {"opening_time": "", "closing_time": "", "full_timing": ""}

    # 1. 24 Hours
    if re.search(r"24\s*hours?", t, re.IGNORECASE):
        return {"opening_time": "12:00 AM", "closing_time": "11:59 PM", "full_timing": "Open 24 Hours"}

    # 2. Time range e.g. "10:00 AM – 8:30 PM" or "10 am - 9 pm"
    m_range = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\s*(?:–|-|to)\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t)
    if m_range:
        op = m_range.group(1).strip().upper()
        cl = m_range.group(2).strip().upper()
        return {
            "opening_time": op,
            "closing_time": cl,
            "full_timing": f"{op} – {cl}"
        }

    # 3. "Open · Closes 9 pm" or "Open · Closes 8:30 pm"
    m_close = re.search(r"closes\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t, re.IGNORECASE)
    if m_close:
        cl_time = m_close.group(1).strip().upper()
        return {
            "opening_time": "",
            "closing_time": cl_time,
            "full_timing": f"Open · Closes {cl_time}"
        }

    # 4. "Closed · Opens 9 am" or "Closed · Opens 9:30 am"
    m_open = re.search(r"opens\s*(?:soon)?\s*(?:[·\-])?\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))", t, re.IGNORECASE)
    if m_open:
        op_time = m_open.group(1).strip().upper()
        return {
            "opening_time": op_time,
            "closing_time": "",
            "full_timing": f"Closed · Opens {op_time}"
        }

    # 5. Just "Open"
    if re.search(r"\bopen(?:\s+now)?\b", t, re.IGNORECASE) and not re.search(r"closed", t, re.IGNORECASE):
        return {
            "opening_time": "",
            "closing_time": "",
            "full_timing": "Open"
        }

    # 6. Just "Closed"
    if re.search(r"\bclosed(?:\s+now)?\b", t, re.IGNORECASE) and not re.search(r"open", t, re.IGNORECASE):
        return {
            "opening_time": "",
            "closing_time": "",
            "full_timing": "Closed"
        }

    return {"opening_time": "", "closing_time": "", "full_timing": t if any(kw in t.lower() for kw in ["am", "pm", "hours", "open", "closed"]) else ""}

def parse_html_card(html_content: str) -> BeautifulSoup:
    return BeautifulSoup(html_content, "html.parser")
