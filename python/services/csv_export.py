"""
Direct CSV Export and Immediate Stream Writer:
Handles schema mappings for Schools, Hospitals, Restaurants, and Generic Businesses,
supports user-defined custom fields, initializes CSV files with UTF-8 BOM, and appends records immediately.
"""

import os
import csv
import re
import threading
from typing import List, Dict, Any, Optional, Set, Tuple

from scraper.record_normalizer import normalize_business_record

SCHOOL_COLUMNS = [
    ("name", "School Name"),
    ("category", "Category"),
    ("address", "Full Address"),
    ("area", "Area"),
    ("city", "City"),
    ("country", "Country"),
    ("pincode", "Pincode/Postcode"),
    ("phone", "Phone Number"),
    ("website", "Website"),
    ("rating", "Google Rating"),
    ("review_count", "Total Reviews"),
    ("opening_time", "Opening Time"),
    ("closing_time", "Closing Time"),
    ("full_timing", "Full Timing"),
    ("source_url", "Google Maps URL"),
    ("latitude", "Latitude"),
    ("longitude", "Longitude"),
    ("search_pincode", "Search Pincode/Postcode"),
    ("search_query", "Search Query"),
    ("scraped_at", "Scraped Date/Time")
]

HOSPITAL_COLUMNS = [
    ("name", "Hospital Name"),
    ("category", "Hospital Type"),
    ("speciality", "Speciality"),
    ("sub_speciality", "Sub Speciality"),
    ("doctor_name", "Doctor Name"),
    ("doctor_speciality", "Doctor Speciality"),
    ("address", "Full Address"),
    ("area", "Area"),
    ("city", "City"),
    ("country", "Country"),
    ("pincode", "Pincode/Postcode"),
    ("phone", "Phone Number"),
    ("website", "Website"),
    ("rating", "Google Rating"),
    ("review_count", "Total Reviews"),
    ("opening_time", "Opening Time"),
    ("closing_time", "Closing Time"),
    ("full_timing", "Full Timing"),
    ("source_url", "Google Maps URL"),
    ("latitude", "Latitude"),
    ("longitude", "Longitude"),
    ("search_pincode", "Search Pincode/Postcode"),
    ("search_query", "Search Query"),
    ("scraped_at", "Scraped Date/Time")
]

RESTAURANT_COLUMNS = [
    ("name", "Restaurant Name"),
    ("category", "Category"),
    ("cuisine_type", "Cuisine Type"),
    ("address", "Full Address"),
    ("area", "Area"),
    ("city", "City"),
    ("country", "Country"),
    ("pincode", "Pincode/Postcode"),
    ("phone", "Phone Number"),
    ("website", "Website"),
    ("rating", "Google Rating"),
    ("review_count", "Total Reviews"),
    ("price_level", "Price Level"),
    ("dine_in_takeaway_delivery", "Dine-in / Takeaway / Delivery"),
    ("popular_dishes", "Popular Dishes"),
    ("opening_time", "Opening Time"),
    ("closing_time", "Closing Time"),
    ("full_timing", "Full Timing"),
    ("source_url", "Google Maps URL"),
    ("latitude", "Latitude"),
    ("longitude", "Longitude"),
    ("search_pincode", "Search Pincode/Postcode"),
    ("search_query", "Search Query"),
    ("scraped_at", "Scraped Date/Time")
]

GENERIC_COLUMNS = [
    ("name", "Business Name"),
    ("entity_type", "Business Type"),
    ("category", "Category"),
    ("sub_category", "Sub Category"),
    ("address", "Full Address"),
    ("area", "Area"),
    ("city", "City"),
    ("country", "Country"),
    ("pincode", "Pincode/Postcode"),
    ("phone", "Phone Number"),
    ("website", "Website"),
    ("rating", "Google Rating"),
    ("review_count", "Total Reviews"),
    ("opening_time", "Opening Time"),
    ("closing_time", "Closing Time"),
    ("full_timing", "Full Timing"),
    ("source_url", "Google Maps URL"),
    ("latitude", "Latitude"),
    ("longitude", "Longitude"),
    ("search_pincode", "Search Pincode/Postcode"),
    ("search_query", "Search Query"),
    ("scraped_at", "Scraped Date/Time")
]

_csv_lock = threading.RLock()

def get_schema_columns(entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    ent = (entity_type or "").lower()
    if "school" in ent or "college" in ent or "academy" in ent:
        cols = list(SCHOOL_COLUMNS)
    elif "hospital" in ent or "clinic" in ent or "doctor" in ent or "dental" in ent:
        cols = list(HOSPITAL_COLUMNS)
    elif "restaurant" in ent or "cafe" in ent or "food" in ent:
        cols = list(RESTAURANT_COLUMNS)
    else:
        cols = list(GENERIC_COLUMNS)

    # Append any user-defined custom fields
    if custom_fields:
        existing_headers = {h.lower() for _, h in cols}
        for field_name in custom_fields:
            clean_name = field_name.strip()
            if clean_name and clean_name.lower() not in existing_headers:
                field_key = re.sub(r"[^a-z0-9]+", "_", clean_name.lower()).strip("_")
                cols.append((field_key, clean_name))

    return cols

def get_csv_headers(entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> List[str]:
    return [col_name for _, col_name in get_schema_columns(entity_type, custom_fields)]

def ensure_csv_file_initialized(file_path: str, entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> bool:
    """Initializes the CSV file with headers if it does not already exist."""
    with _csv_lock:
        try:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                headers = get_csv_headers(entity_type, custom_fields)
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
            return True
        except Exception as e:
            print(f"[CSV Export] Error initializing CSV file {file_path}: {e}")
            return False

def append_record_to_csv(file_path: str, record: Dict[str, Any], entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> bool:
    """Appends a single scraped record dictionary immediately to the target CSV."""
    with _csv_lock:
        try:
            norm_rec = normalize_business_record(record)
            ensure_csv_file_initialized(file_path, entity_type, custom_fields)
            cols = get_schema_columns(entity_type, custom_fields)
            row = []
            for field_key, header_name in cols:
                val = norm_rec.get(field_key)
                if val is None:
                    # Check by header name fallback
                    val = norm_rec.get(header_name, "")
                if isinstance(val, (int, float)):
                    row.append(str(val))
                elif isinstance(val, str):
                    row.append(val.strip())
                elif isinstance(val, list):
                    row.append(", ".join(str(x) for x in val if x))
                else:
                    row.append(str(val) if val is not None else "")

            with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
            return True
        except Exception as e:
            print(f"[CSV Export] Failed to append record to CSV: {e}")
            return False

def load_existing_records_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Reads existing records from CSV if resuming."""
    with _csv_lock:
        records = []
        if not os.path.exists(file_path):
            return records
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(normalize_business_record(dict(row)))
        except Exception as e:
            print(f"[CSV Export] Error reading existing CSV: {e}")
        return records

def write_all_records_to_csv(file_path: str, records: List[Dict[str, Any]], entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> bool:
    """Writes all in-memory records to a CSV file."""
    with _csv_lock:
        try:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            cols = get_schema_columns(entity_type, custom_fields)
            headers = [h for _, h in cols]

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for record in records:
                    norm_rec = normalize_business_record(record)
                    row = []
                    for field_key, header_name in cols:
                        val = norm_rec.get(field_key)
                        if val is None:
                            val = norm_rec.get(header_name, "")
                        if isinstance(val, (int, float)):
                            row.append(str(val))
                        elif isinstance(val, str):
                            row.append(val.strip())
                        elif isinstance(val, list):
                            row.append(", ".join(str(x) for x in val if x))
                        else:
                            row.append(str(val) if val is not None else "")
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"[CSV Export] Failed writing all records to CSV: {e}")
            return False

def normalize_csv_record(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a CSV row dictionary to have standard canonical schema keys.
    """
    return normalize_business_record(row)

def get_history_csv_files(search_dirs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Discovers all CSV files in the workspace / python folder with metadata
    (filename, full path, record count, file size in KB, formatted last modified timestamp).
    """
    with _csv_lock:
        if not search_dirs:
            services_dir = os.path.dirname(os.path.abspath(__file__))
            python_dir = os.path.dirname(services_dir)
            root_dir = os.path.dirname(python_dir)
            
            search_dirs = [
                root_dir,
                os.getcwd(),
                python_dir,
                os.path.join(python_dir, "data"),
                os.path.join(root_dir, "data")
            ]

        seen_paths = set()
        history_files = []

        for d in search_dirs:
            if not os.path.exists(d) or not os.path.isdir(d):
                continue
            try:
                for entry in os.scandir(d):
                    if entry.is_file() and entry.name.lower().endswith(".csv"):
                        norm_path = os.path.abspath(entry.path)
                        if norm_path in seen_paths:
                            continue
                        seen_paths.add(norm_path)

                        try:
                            stat = entry.stat()
                            size_bytes = stat.st_size
                            size_kb = round(size_bytes / 1024, 1)
                            from datetime import datetime
                            mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                            # Count records without reading entire file into memory
                            line_count = 0
                            headers = []
                            with open(norm_path, "r", encoding="utf-8-sig", errors="replace") as f:
                                reader = csv.reader(f)
                                try:
                                    headers = next(reader, [])
                                    for _ in reader:
                                        line_count += 1
                                except Exception:
                                    pass

                            history_files.append({
                                "filename": entry.name,
                                "filepath": norm_path,
                                "record_count": line_count,
                                "size_bytes": size_bytes,
                                "size_formatted": f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 2)} MB",
                                "modified_at": mtime_str,
                                "headers": headers
                            })
                        except Exception as file_err:
                            print(f"[CSV Export] Error reading history file {entry.name}: {file_err}")
            except Exception as dir_err:
                print(f"[CSV Export] Error scanning dir {d}: {dir_err}")

        # Sort newest modified first
        history_files.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
        return history_files

def load_records_from_csv_file(file_path: str) -> Dict[str, Any]:
    """
    Reads a historical CSV file, normalizes the records for the React data table,
    and returns full metadata.
    """
    with _csv_lock:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}", "records": []}

        records = []
        headers = []
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for row in reader:
                    normalized = normalize_csv_record(row)
                    records.append(normalized)

            return {
                "success": True,
                "filepath": os.path.abspath(file_path),
                "filename": os.path.basename(file_path),
                "headers": headers,
                "records": records,
                "count": len(records)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "records": []}

def delete_history_csv_file(file_path: str) -> Dict[str, Any]:
    """
    Safely deletes a specified CSV file.
    """
    with _csv_lock:
        if not os.path.exists(file_path):
            return {"success": False, "error": "File does not exist"}
        try:
            os.remove(file_path)
            return {"success": True, "deleted_path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

def export_records_to_csv(records: List[Dict[str, Any]], target_file_path: str, entity_type: Optional[str] = None, custom_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Helper for exporting records to CSV with status dict."""
    success = write_all_records_to_csv(target_file_path, records, entity_type, custom_fields)
    return {"success": success, "file_path": target_file_path}

