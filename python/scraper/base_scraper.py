"""
Base Scraper Engine:
Defines the strict sequential postcode-by-postcode scraping lifecycle,
semantic detail panel extraction, infinite feed exhaustion, cross-postcode
duplicate management, immediate CSV disk persistence, and real-time live event streaming.
"""

import sys
import time
import json
import uuid
import os
import random
import re
import urllib.parse
from typing import Dict, Any, Optional, Callable, List, Tuple, Set
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException

from .selenium_manager import SeleniumManager
from .duplicate_detector import DuplicateDetector
from .record_normalizer import normalize_business_record, is_valid_category_name, parse_hours
from .bs4_parser import (
    clean_text,
    extract_phone,
    extract_pincode,
    extract_rating,
    extract_review_count,
    extract_timing_components
)
from services.csv_export import (
    ensure_csv_file_initialized,
    append_record_to_csv,
    load_existing_records_from_csv
)

SELECTORS = {
    "results_panel": 'div[role="feed"]',
    "result_card_link": 'a.hfpxzc, a[href*="/maps/place/"]',
    "detail_panel": 'div[role="main"], div.m6QErb.DxyBCb, div.TIHn2',
    "listing_name": "h1.DUwDvf, h1.fontHeadlineLarge, h1",
    "listing_category": "button.DkEaL, button[jsaction*='category'], span.DkEaL",
    "listing_rating": 'div.F7nice span[aria-hidden="true"], span.ceNzKf',
    "listing_reviews": 'div.F7nice span[aria-label*="review"], div.F7nice span:last-child, button[jsaction*="reviews"], span.UY7F9',
    "listing_address_button": 'button[data-item-id="address"], button[aria-label^="Address:"], [data-item-id="address"]',
    "listing_phone_button": 'button[data-item-id^="phone:"], a[href^="tel:"], button[aria-label^="Phone:"]',
    "listing_website_link": 'a[data-item-id="authority"], a[aria-label^="Website:"], a[data-tooltip="Open website"]',
    "listing_hours_section": 'div[data-item-id="oh"], button[data-item-id="oloc"], div.OM3Cfd, div.t39EBf',
}

def extract_lat_lng_from_url(url: str) -> Tuple[Optional[float], Optional[float]]:
    if not url:
        return None, None
    # 1. Standard @lat,lng format
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            pass
    # 2. Google Maps place data payload !3d<lat>!4d<lng>
    match_data = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if match_data:
        try:
            return float(match_data.group(1)), float(match_data.group(2))
        except ValueError:
            pass
    return None, None

def is_rating_str(s: str) -> bool:
    clean = s.strip()
    return bool(re.match(r"^[1-5](\.\d)?$", clean))

def is_review_count_str(s: str) -> bool:
    clean = s.strip()
    return bool(re.match(r"^\(?\d[\d,kK\.]*\)?(\s*(reviews?|ratings?))?$", clean, re.IGNORECASE))

def is_price_str(s: str) -> bool:
    clean = s.strip()
    return bool(re.match(r"^[₹\$€£\s\(\)\·\•]+$", clean))

def is_timing_str(s: str) -> bool:
    low = s.lower().strip()
    timing_keywords = [
        "open", "closed", "closes", "opens", "24 hours", "24 hrs",
        "temporarily closed", "permanently closed", "closes soon", "opens soon",
        "open now", "closed now"
    ]
    return any(kw in low for kw in timing_keywords) and not any(loc_kw in low for loc_kw in ["road", "rd", "street", "nagar", "society", "complex", "highway", "plot", "near", "opp", "circle", "char rasta"])

def is_quote_str(s: str) -> bool:
    clean = s.strip()
    return clean.startswith('"') or clean.startswith('“') or clean.startswith('”') or clean.startswith("· \"") or clean.startswith("· “") or clean.endswith('"') or clean.endswith('”')

def is_service_option_str(s: str) -> bool:
    low = s.lower().strip()
    return any(kw in low for kw in ["dine-in", "takeaway", "delivery", "in-store shopping", "in-store pick-up", "curbside pickup", "wheelchair accessible", "drive-through", "on-site services", "online appointments", "no-contact delivery", "free delivery"])

def is_address_str(s: str) -> bool:
    low = s.lower().strip()
    if re.search(r"\b[2-9CFGHJMPQRVWX]{4}\+[2-9CFGHJMPQRVWX]{2,3}\b", s, re.IGNORECASE):
        return True
    addr_keywords = [
        "road", "rd", "street", "st", "lane", "avenue", "ave", "highway", "hwy",
        "near", "nr", "opp", "opposite", "behind", "next to", "beside",
        "cross", "plot", "nagar", "society", "soc", "marg", "complex", "circle",
        "plaza", "tower", "bazaar", "market", "block", "sector", "phase",
        "colony", "park", "enclave", "gam", "char rasta", "bridge", "rasta",
        "floor", "building", "bldg", "flat", "shop", "office"
    ]
    return any(re.search(r"\b" + re.escape(kw) + r"\b", low) for kw in addr_keywords)

def log_msg(msg: str):
    try:
        sys.stderr.write(f"{msg}\n")
        sys.stderr.flush()
    except Exception:
        pass

class BaseScraper:
    def __init__(
        self,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        headless: bool = True,
        output_csv_path: Optional[str] = None,
        existing_records: Optional[List[Dict[str, Any]]] = None,
        custom_fields: Optional[List[str]] = None
    ):
        self.event_callback = event_callback or self._default_callback
        self.headless = headless
        self.output_csv_path = output_csv_path
        self.selenium_mgr = SeleniumManager(headless=self.headless)
        self.duplicate_detector = DuplicateDetector()
        self.is_stopped = False
        
        # Authoritative in-memory session stats
        self.in_memory_records: List[Dict[str, Any]] = []
        self.stats = {
            "found": 0,
            "collected": 0,
            "duplicates": 0,
            "failed": 0,
            "progress_pct": 0.0,
            "current_pincode": "",
            "pincode_index": 0,
            "pincode_total": 0
        }

        self.custom_fields = custom_fields or []

        # Initialize CSV header if output path provided
        if self.output_csv_path:
            ensure_csv_file_initialized(self.output_csv_path, self.get_entity_type(), self.custom_fields)
            existing_recs = load_existing_records_from_csv(self.output_csv_path)
            for rec in existing_recs:
                self.duplicate_detector.register(rec)

        if existing_records:
            self.add_existing_hashes(existing_records)

    def get_entity_type(self) -> str:
        return "business"

    def set_custom_fields(self, fields: List[str]):
        self.custom_fields = fields or []

    def set_output_csv(self, path: str, custom_fields: Optional[List[str]] = None):
        self.output_csv_path = path
        if custom_fields is not None:
            self.custom_fields = custom_fields
        if path:
            ensure_csv_file_initialized(path, self.get_entity_type(), self.custom_fields)
            existing_recs = load_existing_records_from_csv(path)
            for rec in existing_recs:
                self.duplicate_detector.register(rec)

    def _default_callback(self, event_type: str, data: Dict[str, Any]):
        payload = {"event": event_type, "data": data, "timestamp": datetime.now().isoformat()}
        try:
            line = json.dumps(payload, ensure_ascii=True)
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        except Exception:
            pass

    def emit(self, event_type: str, data: Dict[str, Any]):
        self.event_callback(event_type, data)

    def stop(self):
        log_msg("\n[Scraper Engine] Stop signal received. Shutting down gracefully...")
        self.is_stopped = True
        self.selenium_mgr.safe_quit()

    def add_existing_hashes(self, existing_records: List[Dict[str, Any]]):
        for rec in existing_records:
            self.duplicate_detector.register(rec)

    def process_record(self, record: Dict[str, Any]) -> bool:
        """
        Validates, deduplicates, writes immediately to disk CSV with flush,
        and broadcasts to UI.
        """
        if not record or not record.get("name"):
            return False

        if not record.get("id"):
            record["id"] = str(uuid.uuid4())
            
        record["scraped_at"] = record.get("scraped_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stats["found"] += 1

        # Check duplicate
        if self.duplicate_detector.is_duplicate(record):
            self.stats["duplicates"] += 1
            name = record.get("name") or record.get("Business Name") or ""
            reason = self.duplicate_detector.get_duplicate_reason(record)
            dup_entry = {
                "id": record.get("id") or str(uuid.uuid4()),
                "name": name,
                "category": record.get("category") or record.get("entity_type") or self.get_entity_type().title(),
                "address": record.get("address", ""),
                "city": record.get("city", ""),
                "area": record.get("area", ""),
                "pincode": record.get("pincode") or record.get("search_pincode", ""),
                "phone": record.get("phone", ""),
                "source_url": record.get("source_url", ""),
                "reason": reason,
                "skipped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Skipped Duplicate"
            }
            log_msg(f"    [DUPLICATE SKIPPED] {name} ({reason})")
            self.emit("duplicate", {
                "record": dup_entry,
                "name": name,
                "phone": record.get("phone"),
                "pincode": record.get("pincode"),
                "stats": self.stats
            })
            return False

        # Register in duplicate detector
        self.duplicate_detector.register(record)
        self.stats["collected"] += 1
        self.in_memory_records.append(record)

        # IMMEDIATELY write record to disk CSV file
        if self.output_csv_path:
            append_record_to_csv(
                self.output_csv_path,
                record,
                record.get("entity_type") or self.get_entity_type(),
                self.custom_fields
            )

        name = record.get("name") or record.get("Business Name") or ""
        log_msg(f"    [SAVED TO CSV] {name} (Written: {self.stats['collected']})")

        # Emit record live to UI
        self.emit("record", {
            "record": record,
            "stats": self.stats
        })
        return True

    def build_pincode_query(self, item: Dict[str, Any]) -> str:
        """
        Builds a localized Google Maps search query:
        e.g. 'coaching in 360001 Rajkot', 'restaurants in LE18 Sheffield', 'hospitals in Satellite 380015 Ahmedabad'
        """
        entity_label = item.get("entity_label") or item.get("entity_type") or self.get_entity_type()
        speciality = item.get("speciality", "")
        city = item.get("city", "")
        area = item.get("area", "")
        pincode = item.get("pincode", "")
        country = item.get("country", "")
        keyword = item.get("keyword", "")

        if speciality:
            entity_term = speciality
            if "hospital" not in speciality.lower() and "clinic" not in speciality.lower():
                entity_term = f"{speciality} clinics"
        elif entity_label:
            entity_term = entity_label
        else:
            entity_term = "business"

        loc_parts = []
        if area:
            loc_parts.append(area)
        if pincode:
            loc_parts.append(str(pincode))
        if city:
            loc_parts.append(city)
        if country and country.lower() not in ["india"]:
            loc_parts.append(country)

        location_str = " ".join(loc_parts).strip()
        if location_str:
            query = f"{entity_term} in {location_str}"
        else:
            query = entity_term

        if keyword and keyword.lower() not in query.lower():
            query = f"{query} {keyword}"

        return query.strip()

    def scrape_queue(
        self,
        queue: List[Dict[str, Any]],
        max_results_per_pincode: Optional[int] = None,
        max_retries_per_pincode: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Strict Sequential Postcode-by-Postcode Execution:
        Postcode 1: First Result -> Last Result -> COMPLETE
        ONLY THEN Postcode 2: First Result -> Last Result -> COMPLETE
        ...
        Until the last postcode.
        """
        total_pincodes = len(queue)
        self.stats["pincode_total"] = total_pincodes

        self.emit("status", {
            "status": "queue_started",
            "total_pincodes": total_pincodes,
            "output_csv": self.output_csv_path
        })

        driver = None
        try:
            driver = self.selenium_mgr.create_driver()

            for idx, item in enumerate(queue, start=1):
                if self.is_stopped:
                    break

                pincode = str(item.get("pincode", ""))
                query = self.build_pincode_query(item)

                log_msg("\n" + "=" * 50)
                log_msg(f"POSTCODE {idx}/{total_pincodes}: {pincode}")
                log_msg("=" * 50)
                log_msg(f"Searching: {query}\n")

                self.stats["current_pincode"] = pincode
                self.stats["pincode_index"] = idx
                self.stats["progress_pct"] = round(((idx - 1) / total_pincodes) * 100, 1)

                self.emit("pincode_start", {
                    "pincode": pincode,
                    "index": idx,
                    "total": total_pincodes,
                    "city": item.get("city", ""),
                    "area": item.get("area", ""),
                    "stats": self.stats
                })

                succeeded = False
                for attempt in range(1, max_retries_per_pincode + 1):
                    if self.is_stopped:
                        break
                    try:
                        self.scrape_single_pincode(driver, item)
                        succeeded = True
                        break
                    except Exception as pin_err:
                        log_msg(f"[Warning] Postcode {pincode} attempt {attempt} failed: {pin_err}")
                        self.emit("pincode_retry", {
                            "pincode": pincode,
                            "attempt": attempt,
                            "max_retries": max_retries_per_pincode,
                            "error": str(pin_err)
                        })
                        time.sleep(2.0)

                if succeeded:
                    log_msg("\n" + "=" * 50)
                    log_msg(f"POSTCODE {pincode} COMPLETE")
                    log_msg(f"Written to CSV: {self.stats['collected']} | Duplicates: {self.stats['duplicates']} | Failed: {self.stats['failed']}")
                    log_msg("=" * 50 + "\n")

                    self.emit("pincode_complete", {
                        "pincode": pincode,
                        "index": idx,
                        "total": total_pincodes,
                        "stats": self.stats
                    })
                else:
                    self.stats["failed"] += 1
                    log_msg(f"[Error] Postcode {pincode} failed all {max_retries_per_pincode} attempts.\n")
                    self.emit("pincode_failed", {
                        "pincode": pincode,
                        "index": idx,
                        "total": total_pincodes,
                        "stats": self.stats
                    })

                # Short polite pause between postcodes
                time.sleep(1.0)

            self.stats["progress_pct"] = 100.0
            log_msg("\n>>> ALL POSTCODES COMPLETED SUCCESSFULLY <<<")
            self.emit("status", {
                "status": "completed" if not self.is_stopped else "stopped",
                "stats": self.stats,
                "output_csv": self.output_csv_path
            })

        except Exception as e:
            log_msg(f"[Scraper Error] Fatal error in scrape_queue: {e}")
            self.emit("error", {"error": str(e), "stats": self.stats})
        finally:
            self.selenium_mgr.safe_quit()

        return self.in_memory_records

    def extract_from_detail_panel(
        self,
        driver,
        item: Dict[str, Any],
        card_href: str,
        card_label: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extracts structured fields directly from the active Google Maps Business Detail panel (div[role="main"]).
        Uses semantic labels, aria-labels, and specific data-item-id attributes.
        """
        try:
            # Locate Detail Panel container (div[role="main"])
            panel_root = driver
            try:
                main_elem = driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')
                if main_elem:
                    panel_root = main_elem
            except Exception:
                panel_root = driver

            # 1. Name
            name = ""
            for name_sel in ["h1.DUwDvf", "h1.fontHeadlineLarge", "h1"]:
                try:
                    elem = panel_root.find_element(By.CSS_SELECTOR, name_sel)
                    if elem and elem.text.strip():
                        candidate = clean_text(elem.text)
                        # Reject Google Maps search feed header 'Results'
                        if candidate.lower() not in ["results", "search results", "all results", "explore results"] and not candidate.lower().startswith("results for"):
                            name = candidate
                            break
                except Exception:
                    pass

            if not name or name.lower() in ["results", "search results", "all results"]:
                name = clean_text(card_label)

            # 2. Category & Sub Category
            category = ""
            sub_category = ""
            try:
                cat_elems = panel_root.find_elements(By.CSS_SELECTOR, "button.DkEaL, button[jsaction*='category'], span.DkEaL")
                for cat_elem in cat_elems:
                    txt = clean_text(cat_elem.text)
                    if is_valid_category_name(txt):
                        if not category:
                            category = txt
                        elif not sub_category and txt.lower() != category.lower():
                            sub_category = txt
                            break
            except Exception:
                pass

            # 3. Rating & Reviews
            rating = None
            reviews = None
            try:
                rating_elem = driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"], span.ceNzKf')
                if rating_elem:
                    rating = extract_rating(rating_elem.text or rating_elem.get_attribute("aria-label"))
            except Exception:
                pass

            try:
                rev_elems = driver.find_elements(By.CSS_SELECTOR, 'div.F7nice span[aria-label*="review"], div.F7nice span:last-child, button[jsaction*="reviews"], span.UY7F9')
                for rev_elem in rev_elems:
                    r_txt = rev_elem.text or rev_elem.get_attribute("aria-label") or ""
                    r_val = extract_review_count(r_txt)
                    if r_val is not None:
                        reviews = r_val
                        break
            except Exception:
                pass

            # 4. Address
            address = ""
            try:
                addr_elem = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"], button[aria-label^="Address:"], [data-item-id="address"]')
                if addr_elem:
                    # Check aria-label first
                    aria = addr_elem.get_attribute("aria-label") or ""
                    if aria.lower().startswith("address:"):
                        address = clean_text(aria[8:])
                    if not address:
                        try:
                            inner = addr_elem.find_element(By.CSS_SELECTOR, "div.Io6YTe, div.fontBodyMedium")
                            address = clean_text(inner.text)
                        except Exception:
                            address = clean_text(addr_elem.text)
            except Exception:
                pass

            # 5. Phone Number
            phone = ""
            try:
                phone_elem = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id^="phone:"], a[href^="tel:"], button[aria-label^="Phone:"]')
                if phone_elem:
                    data_id = phone_elem.get_attribute("data-item-id") or ""
                    if "phone:tel:" in data_id:
                        phone = clean_text(data_id.replace("phone:tel:", ""))
                    if not phone:
                        aria = phone_elem.get_attribute("aria-label") or ""
                        if aria.lower().startswith("phone:"):
                            phone = clean_text(aria[6:])
                    if not phone:
                        try:
                            inner = phone_elem.find_element(By.CSS_SELECTOR, "div.Io6YTe, div.fontBodyMedium")
                            phone = clean_text(inner.text)
                        except Exception:
                            phone = clean_text(phone_elem.text)
            except Exception:
                pass

            # 6. Website
            website = ""
            try:
                web_elem = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"], a[aria-label^="Website:"], a[data-tooltip="Open website"]')
                if web_elem:
                    href = web_elem.get_attribute("href") or ""
                    if href.startswith("http") and "google.com/maps" not in href.lower():
                        website = clean_text(href)
            except Exception:
                pass

            # 7. Timings / Hours
            timing_str = ""
            try:
                hours_elem = driver.find_element(By.CSS_SELECTOR, 'div[data-item-id="oh"], button[data-item-id="oloc"], div.OM3Cfd')
                if hours_elem:
                    aria = hours_elem.get_attribute("aria-label") or ""
                    if aria and is_timing_str(aria):
                        timing_str = clean_text(aria)
                    if not timing_str:
                        timing_str = clean_text(hours_elem.text)
            except Exception:
                pass

            # Check weekly hours table if present
            try:
                table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.eKjhZj tr, table.mMx2Re tr, div.t39EBf table tr')
                if table_rows:
                    day_timings = []
                    for row in table_rows:
                        row_txt = clean_text(row.text)
                        if row_txt:
                            day_timings.append(row_txt)
                    if day_timings:
                        timing_str = " | ".join(day_timings)
            except Exception:
                pass

            # 8. Coordinates & URL
            current_url = driver.current_url or card_href
            lat, lng = extract_lat_lng_from_url(current_url)
            if lat is None or lng is None:
                lat, lng = extract_lat_lng_from_url(card_href)

            source_url = ""
            if current_url and current_url.startswith("http") and ("google.com/maps" in current_url or "/maps/place/" in current_url):
                source_url = current_url
            elif card_href and card_href.startswith("http"):
                source_url = card_href

            # Build raw listing dictionary
            raw_dict = {
                "name": name,
                "category": category,
                "sub_category": sub_category,
                "address": address,
                "area": item.get("area", ""),
                "city": item.get("city", ""),
                "country": item.get("country", "India"),
                "pincode": str(item.get("pincode", "")),
                "search_pincode": str(item.get("pincode", "")),
                "phone": phone,
                "website": website,
                "rating": rating,
                "review_count": reviews,
                "timing_str": timing_str,
                "source_url": source_url,
                "latitude": lat,
                "longitude": lng,
                "search_query": self.build_pincode_query(item)
            }

            return normalize_business_record(raw_dict, query_context=item)

        except Exception as e:
            log_msg(f"  [Warning] Detail panel extraction error: {e}")
            return None

    def parse_card_soup(
        self,
        soup: BeautifulSoup,
        href: str,
        listing_label: str,
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback card parser: Extracts structured fields directly from feed listing card.
        Strictly prevents review counts, ratings, or timing from contaminating category or address.
        """
        entity_type = item.get("entity_type", "business")
        category_hint = item.get("category", "")
        city = item.get("city", "")
        area = item.get("area", "")
        search_pincode = str(item.get("pincode", ""))
        country = item.get("country", "India")

        full_text = soup.get_text(separator=" | ")

        # 1. Name
        name_elem = soup.select_one("div.qBF1Pd, div.fontHeadlineSmall, h3")
        name = clean_text(name_elem.get_text()) if name_elem else clean_text(listing_label)
        if not name or name.lower() in ["results", "search results", "all results", "explore results"] or name.lower().startswith("results for"):
            name = clean_text(listing_label)

        # 2. Rating & Reviews
        rating_elem = soup.select_one("span.MW4etd, span.Z3HNkc")
        rating = extract_rating(rating_elem.get_text()) if rating_elem else extract_rating(full_text)

        reviews_elem = soup.select_one("span.UY7F9")
        reviews = None
        if reviews_elem:
            reviews = extract_review_count(reviews_elem.get_text())
        if reviews is None:
            reviews = extract_review_count(full_text)

        # 3. Leaf Block Analysis
        all_w4 = soup.select("div.W4Efsd")
        leaf_blocks = [b for b in all_w4 if not b.select("div.W4Efsd")]
        if not leaf_blocks and all_w4:
            leaf_blocks = all_w4

        scraped_category = ""
        cuisine_type = ""
        address = ""
        phone = ""
        timing_str = ""
        price_level = ""
        services_list = []
        candidate_address_parts = []

        CUISINE_KEYWORDS = [
            "indian", "south indian", "north indian", "gujarati", "punjabi",
            "chinese", "italian", "continental", "mexican", "fast food", "street food",
            "mughlai", "kathiyawadi", "marwari", "rajasthani", "bengali", "thai",
            "pizza", "biryani", "seafood", "vegetarian", "pure veg", "non-vegetarian"
        ]

        for block in leaf_blocks:
            block_text = clean_text(block.get_text(separator=" · "))
            if not block_text:
                continue

            # Check phone in block
            ph = extract_phone(block_text)
            if ph and not phone:
                phone = ph

            # Check price level in block
            if not price_level:
                if "₹₹₹₹" in block_text or "$$$$" in block_text:
                    price_level = "₹₹₹₹ (Very Expensive)"
                elif "₹₹₹" in block_text or "$$$" in block_text:
                    price_level = "₹₹₹ (Expensive)"
                elif "₹₹" in block_text or "$$" in block_text:
                    price_level = "₹₹ (Moderate)"
                elif "₹" in block_text or "$" in block_text:
                    price_level = "₹ (Inexpensive)"

            # Check service options
            for s_kw in ["Dine-in", "Takeaway", "Delivery", "No-contact delivery", "Curbside pickup", "In-store shopping"]:
                if re.search(r"\b" + re.escape(s_kw) + r"\b", block_text, re.IGNORECASE):
                    if s_kw not in services_list:
                        services_list.append(s_kw)

            # Check if block is the timing row
            if is_timing_str(block_text):
                if not timing_str:
                    timing_str = block_text
                # Never extract address or category from timing row!
                continue

            # Spans in this leaf block
            spans = block.select("span")
            tokens = []
            if spans:
                for sp in spans:
                    t = clean_text(sp.get_text())
                    if t and t not in ["·", "•", "|", "-"]:
                        tokens.append(t)
            else:
                tokens = [clean_text(t) for t in block_text.split("·") if clean_text(t)]

            for token in tokens:
                token_clean = token.strip(" ·•|,-")
                if not token_clean:
                    continue

                ph_tok = extract_phone(token_clean)
                if ph_tok and not phone:
                    phone = ph_tok
                    continue

                # Skip rating, reviews, parens digits (e.g. (255), (31), (1,907), (14))
                if is_rating_str(token_clean) or is_review_count_str(token_clean) or re.match(r"^\(?\d+[\d,kK\.]*\)?$", token_clean):
                    continue

                # Skip price, quotes, service options
                if is_price_str(token_clean) or is_quote_str(token_clean) or is_service_option_str(token_clean):
                    continue

                # Check if timing string
                if is_timing_str(token_clean):
                    if not timing_str:
                        timing_str = token_clean
                    continue

                # Check Cuisine detection
                tok_low = token_clean.lower()
                if not cuisine_type and any(c_kw == tok_low or f"{c_kw} restaurant" in tok_low for c_kw in CUISINE_KEYWORDS):
                    cuisine_type = token_clean.replace("Restaurant", "").replace("restaurant", "").strip().title()

                # Check Category identification (must be validated genuine category)
                if not scraped_category and is_valid_category_name(token_clean):
                    if not is_address_str(token_clean):
                        scraped_category = token_clean
                        continue

                # Otherwise, consider as address/location part
                if not is_timing_str(token_clean) and not is_review_count_str(token_clean) and not re.match(r"^\(?\d+[\d,kK\.]*\)?$", token_clean):
                    candidate_address_parts.append(token_clean)

        # Assemble address from candidate parts
        if candidate_address_parts:
            clean_parts = []
            for p in candidate_address_parts:
                p_clean = p
                if phone:
                    p_clean = p_clean.replace(phone, "").strip(" ,·-")
                if scraped_category and p_clean.lower() == scraped_category.lower():
                    continue
                if cuisine_type and p_clean.lower() == cuisine_type.lower():
                    continue
                if is_timing_str(p_clean):
                    continue
                if p_clean and p_clean not in clean_parts:
                    clean_parts.append(p_clean)
            if clean_parts:
                address = ", ".join(clean_parts)

        # Phone fallback
        if not phone:
            phone = extract_phone(full_text)

        # Website
        website = ""
        web_elem = soup.select_one('a[data-value="Website"], a[aria-label*="Website"], a.lcr4fd')
        if web_elem:
            website = web_elem.get("href", "")

        # Coordinates
        lat, lng = extract_lat_lng_from_url(href)

        # Validate Maps URL
        source_url = ""
        if href and str(href).startswith("http") and ("google.com/maps" in str(href) or "maps.google" in str(href) or "/maps/place/" in str(href)):
            source_url = clean_text(href)

        raw_dict = {
            "name": name,
            "category": scraped_category or (f"{cuisine_type} Restaurant" if cuisine_type else "") or category_hint,
            "sub_category": cuisine_type or item.get("entity_label") or category_hint,
            "cuisine_type": cuisine_type,
            "address": address,
            "area": area,
            "city": city,
            "country": country,
            "pincode": search_pincode,
            "search_pincode": search_pincode,
            "phone": phone,
            "website": website,
            "rating": rating,
            "review_count": reviews,
            "price_level": price_level,
            "dine_in_takeaway_delivery": " · ".join(services_list) if services_list else "",
            "popular_dishes": "",
            "timing_str": timing_str,
            "source_url": source_url,
            "latitude": lat,
            "longitude": lng,
            "search_query": self.build_pincode_query(item)
        }

        # Normalize via central canonical record normalizer
        rec = normalize_business_record(raw_dict, query_context=item)

        # Entity-specific medical/doctor extraction
        if entity_type == "hospital" or "hospital" in rec["category"].lower() or "clinic" in rec["category"].lower():
            rec["speciality"] = item.get("speciality", "") or rec["category"]
            doc_m = re.search(r"\b(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", full_text)
            rec["doctor_name"] = clean_text(doc_m.group(1)) if doc_m else ""
            rec["doctor_speciality"] = rec["speciality"]
        return rec

    def extract_listing_details(
        self,
        soup: BeautifulSoup,
        full_text: str,
        href: str,
        listing_label: str,
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detailed single page listing extractor."""
        return self.parse_card_soup(soup, href, listing_label, item)

    def scrape_single_pincode(self, driver, item: Dict[str, Any]):
        """
        Progressive Live Streaming Single Postcode Scraping:
        1. Searches Google Maps for `<entity> in <pincode> <city>`
        2. Iterates through search results:
           - Opens business details panel for high-fidelity extraction
           - Falls back to card parsing if detail panel is unavailable
           - Checks duplicate detector
           - Appends immediately to disk CSV file
           - Emits live "record" event to DataTable in real time
        3. Scrolls smoothly until the feed is genuinely exhausted.
        """
        query = self.build_pincode_query(item)
        pincode = str(item.get("pincode", ""))

        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/maps/search/{encoded_query}?hl=en"

        self.emit("status", {
            "status": "navigating",
            "query": query,
            "pincode": pincode,
            "url": search_url
        })
        driver.get(search_url)

        # Wait for either result feed or direct single listing card
        try:
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["results_panel"])),
                    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["listing_name"]))
                )
            )
        except TimeoutException:
            log_msg(f"  No results loaded for {query}.")
            return

        time.sleep(1.5)

        # 1. Check if single listing directly loaded
        single_name_elem = None
        try:
            single_name_elem = driver.find_element(By.CSS_SELECTOR, SELECTORS["listing_name"])
        except Exception:
            pass

        feed_elem = None
        try:
            feed_elem = driver.find_element(By.CSS_SELECTOR, SELECTORS["results_panel"])
        except Exception:
            pass

        if not feed_elem and single_name_elem:
            record = self.extract_from_detail_panel(driver, item, driver.current_url, single_name_elem.text)
            if not record:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                full_text = soup.get_text(separator=" | ")
                record = self.extract_listing_details(soup, full_text, driver.current_url, single_name_elem.text, item)
            self.process_record(record)
            return

        if not feed_elem:
            log_msg(f"  0 listings found for {pincode}.")
            return

        log_msg(f"Streaming live results for postal code {pincode}...")
        processed_hrefs: Set[str] = set()
        no_change_count = 0
        MAX_NO_CHANGE_STREAK = 7
        SCROLL_PAUSE = 1.0

        while not self.is_stopped:
            # 1. Harvest currently loaded card elements from DOM
            try:
                card_link_elems = driver.find_elements(By.CSS_SELECTOR, SELECTORS["result_card_link"])
            except Exception:
                card_link_elems = []

            new_records_in_pass = 0

            for link_elem in card_link_elems:
                if self.is_stopped:
                    break
                try:
                    href = link_elem.get_attribute("href")
                    label = clean_text(link_elem.get_attribute("aria-label") or "")

                    if not href or href in processed_hrefs:
                        continue

                    processed_hrefs.add(href)

                    # Get parent card element container for fallback parsing
                    card_html = ""
                    card_parent = None
                    try:
                        card_parent = link_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'Nv2PK') or contains(@class, 'bfDCEb') or contains(@class, 'THOPZb') or @role='article'][1]")
                        card_html = card_parent.get_attribute("outerHTML")
                    except Exception:
                        try:
                            card_html = link_elem.get_attribute("outerHTML")
                        except Exception:
                            pass

                    if not label or label.lower() in ["results", "search results", "all results"]:
                        if card_parent:
                            try:
                                title_elem = card_parent.find_element(By.CSS_SELECTOR, "div.qBF1Pd, div.fontHeadlineSmall, h3")
                                if title_elem and title_elem.text.strip():
                                    cand_label = clean_text(title_elem.text)
                                    if cand_label.lower() not in ["results", "search results", "all results"]:
                                        label = cand_label
                            except Exception:
                                pass

                    # Step A: Click to open detail panel for authoritative extraction
                    record = None
                    try:
                        driver.execute_script("arguments[0].click();", link_elem)
                        time.sleep(0.5)
                        record = self.extract_from_detail_panel(driver, item, href, label)
                    except Exception as click_err:
                        pass

                    # Step B: If detail panel extraction was not complete, fall back to card soup
                    if not record or not record.get("name") or not record.get("address"):
                        card_soup = BeautifulSoup(card_html, "html.parser") if card_html else BeautifulSoup(f"<div><h3>{label}</h3></div>", "html.parser")
                        fallback_rec = self.parse_card_soup(card_soup, href, label, item)
                        if not record:
                            record = fallback_rec
                        else:
                            # Merge missing fields from card soup if detail panel missed something
                            for k, v in fallback_rec.items():
                                if not record.get(k) and v:
                                    record[k] = v

                    if not record or not record.get("name"):
                        continue

                    # Process record: checks duplicate -> writes directly to CSV -> streams directly to DataTable live!
                    saved = self.process_record(record)
                    if saved:
                        new_records_in_pass += 1
                        self.emit("listing_progress", {
                            "pincode": pincode,
                            "listing_index": self.stats["collected"],
                            "listing_total": len(processed_hrefs),
                            "label": record.get("name", "")
                        })

                except StaleElementReferenceException:
                    continue
                except Exception as card_err:
                    log_msg(f"  [Warning] Card parse error: {card_err}")
                    continue

            # 2. Check for explicit end-of-results indicator in feed text
            feed_text = ""
            try:
                feed_text = feed_elem.text.lower()
            except Exception:
                pass

            end_marker_detected = (
                "you've reached the end of the list" in feed_text
                or "no more results" in feed_text
                or "you've reached the end" in feed_text
            )

            if new_records_in_pass > 0:
                no_change_count = 0
            else:
                no_change_count += 1

            if end_marker_detected and no_change_count >= 2:
                log_msg(f"  [End of Results] Reached end of Google Maps feed for {pincode}.")
                break

            if no_change_count >= MAX_NO_CHANGE_STREAK:
                log_msg(f"  [Feed Complete] All listings processed for {pincode} ({self.stats['collected']} saved).")
                break

            # 3. Scroll down feed to reveal next batch of listings
            try:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", feed_elem)
            except Exception:
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                except Exception:
                    pass

            time.sleep(SCROLL_PAUSE)
