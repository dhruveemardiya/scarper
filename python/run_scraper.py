"""
Python Scraper Bridge Runner:
Listens on stdin for line-delimited JSON requests from Electron main process,
dispatches to NLP parser, suggestion engine, sequential pincode scrapers, and CSV exporter,
and writes line-delimited JSON events to stdout.
"""

import sys
import os
import json
import threading
import traceback
from typing import Dict, Any, Optional, List

# Ensure python directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from services.nlp_parser import parse_search_query
from services.suggestion_service import generate_suggestions
from services.geo_data import get_pincodes_for_city_area, get_areas_for_city
from services.csv_export import (
    export_records_to_csv,
    write_all_records_to_csv,
    get_history_csv_files,
    load_records_from_csv_file,
    delete_history_csv_file
)
from scraper.restaurant_scraper import RestaurantScraper
from scraper.hospital_scraper import HospitalScraper
from scraper.generic_scraper import GenericScraper
from network_server import start_network_bridge, state_manager, broadcast_event

active_scraper = None
active_thread = None

def send_response(response_type: str, data: Any, req_id: Optional[str] = None):
    payload = {
        "type": response_type,
        "data": data,
        "req_id": req_id
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()

def handle_ping(req: Dict[str, Any]):
    send_response("pong", {"status": "ok", "message": "Python scraper engine connected successfully!"}, req.get("id"))

def handle_parse_query(req: Dict[str, Any]):
    query = req.get("query", "")
    parsed = parse_search_query(query)
    suggestions = generate_suggestions(parsed)
    send_response("query_parsed", {
        "parsed": parsed,
        "suggestions": suggestions
    }, req.get("id"))

def handle_get_suggestions(req: Dict[str, Any]):
    parsed = req.get("parsed") or parse_search_query(req.get("query", ""))
    suggestions = generate_suggestions(parsed)
    send_response("suggestions", suggestions, req.get("id"))

def handle_get_pincodes(req: Dict[str, Any]):
    city = req.get("city", "")
    area = req.get("area", "")
    pincodes = get_pincodes_for_city_area(city, area)
    send_response("pincodes", {"city": city, "area": area, "pincodes": pincodes}, req.get("id"))

def handle_export_csv(req: Dict[str, Any]):
    records = req.get("records", [])
    target_path = req.get("target_file_path", "")
    entity_type = req.get("entity_type", "business")
    custom_fields = req.get("custom_fields", [])
    success = write_all_records_to_csv(target_path, records, entity_type, custom_fields)
    send_response("csv_exported", {"success": success, "file_path": target_path}, req.get("id"))

def handle_get_history(req: Dict[str, Any]):
    files = get_history_csv_files()
    send_response("history_files", {"files": files, "count": len(files)}, req.get("id"))

def handle_load_csv(req: Dict[str, Any]):
    file_path = req.get("filepath") or req.get("filename") or ""
    res = load_records_from_csv_file(file_path)
    if res.get("success"):
        with state_manager.lock:
            state_manager.records = res.get("records", [])
            state_manager.output_csv_path = res.get("filepath", "")
            state_manager.stats["collected"] = len(res.get("records", []))
            state_manager.status_message = f"Loaded {len(res.get('records', []))} records from {os.path.basename(file_path)}"
        broadcast_event("status", {
            "status": "csv_loaded",
            "count": len(res.get("records", [])),
            "output_csv_path": res.get("filepath", "")
        })
    send_response("csv_loaded", res, req.get("id"))

def handle_delete_csv(req: Dict[str, Any]):
    file_path = req.get("filepath") or req.get("filename") or ""
    res = delete_history_csv_file(file_path)
    send_response("csv_deleted", res, req.get("id"))

def run_scraping_worker(
    queue: List[Dict[str, Any]],
    output_csv_path: Optional[str],
    max_results_per_pincode: int,
    existing_records: list,
    custom_fields: Optional[List[str]],
    req_id: str
):
    global active_scraper
    if not queue:
        send_response("scraper_event", {
            "event": "error",
            "data": {"error": "Pincode queue is empty. Please select at least one pincode/postcode."}
        }, req_id)
        return

    first_item = queue[0]
    entity_type = (first_item.get("entity_type") or "business").lower()

    def event_cb(event_name: str, data: Dict[str, Any]):
        send_response("scraper_event", {
            "event": event_name,
            "data": data
        }, req_id)

    try:
        if "restaurant" in entity_type or "cafe" in entity_type or "food" in entity_type:
            scraper = RestaurantScraper(
                event_callback=event_cb,
                headless=True,
                output_csv_path=output_csv_path
            )
        elif "hospital" in entity_type or "clinic" in entity_type or "doctor" in entity_type:
            scraper = HospitalScraper(
                event_callback=event_cb,
                headless=True,
                output_csv_path=output_csv_path
            )
        else:
            scraper = GenericScraper(
                event_callback=event_cb,
                headless=True,
                output_csv_path=output_csv_path
            )

        active_scraper = scraper
        if custom_fields:
            scraper.set_custom_fields(custom_fields)
            if output_csv_path:
                scraper.set_output_csv(output_csv_path, custom_fields)

        if existing_records:
            scraper.add_existing_hashes(existing_records)

        scraper.scrape_queue(queue, max_results_per_pincode=max_results_per_pincode)
    except Exception as e:
        err_msg = traceback.format_exc()
        send_response("scraper_event", {
            "event": "error",
            "data": {"error": str(e), "traceback": err_msg}
        }, req_id)
    finally:
        active_scraper = None

def handle_start_scraping(req: Dict[str, Any]):
    global active_scraper, active_thread
    if active_scraper:
        try:
            active_scraper.stop()
        except Exception:
            pass

    # Accepts queue of pincodes or single params
    queue = req.get("queue")
    if not queue:
        params = req.get("params", {})
        pincodes = params.get("pincodes") or ([params["pincode"]] if params.get("pincode") else [""])
        queue = []
        for p in pincodes:
            item = dict(params)
            item["pincode"] = p
            queue.append(item)

    output_csv_path = req.get("output_csv_path") or req.get("target_file_path")
    max_results_per_pincode = int(req.get("max_results_per_pincode") or req.get("max_results", 100))
    existing_records = req.get("existing_records", [])
    custom_fields = req.get("custom_fields", [])
    req_id = req.get("id", "")

    active_thread = threading.Thread(
        target=run_scraping_worker,
        args=(queue, output_csv_path, max_results_per_pincode, existing_records, custom_fields, req_id),
        daemon=True
    )
    active_thread.start()
    send_response("scraping_started", {
        "status": "started",
        "queue_length": len(queue),
        "output_csv_path": output_csv_path
    }, req_id)

def handle_stop_scraping(req: Dict[str, Any]):
    global active_scraper
    if active_scraper:
        scraper_to_stop = active_scraper
        threading.Thread(target=scraper_to_stop.stop, daemon=True).start()
    send_response("scraping_stopped", {"status": "stopped"}, req.get("id"))

COMMAND_HANDLERS = {
    "ping": handle_ping,
    "parse_query": handle_parse_query,
    "get_suggestions": handle_get_suggestions,
    "get_pincodes": handle_get_pincodes,
    "start_scraping": handle_start_scraping,
    "stop_scraping": handle_stop_scraping,
    "export_csv": handle_export_csv,
    "get_history": handle_get_history,
    "load_csv": handle_load_csv,
    "delete_csv": handle_delete_csv
}

def main():
    # Start unified HTTP/WebSocket network server in background thread on 0.0.0.0:8765
    try:
        start_network_bridge()
    except Exception as e:
        sys.stderr.write(f"[Python] Could not launch network bridge: {e}\n")

    # Signal readiness immediately
    send_response("ready", {"version": "2.0.0", "status": "initialized"})

    for line in sys.stdin:
        if not line or not line.strip():
            continue
        try:
            req = json.loads(line.strip())
            action = req.get("action")
            handler = COMMAND_HANDLERS.get(action)
            if handler:
                handler(req)
            else:
                send_response("error", {"error": f"Unknown action: {action}"}, req.get("id"))
        except Exception as e:
            send_response("error", {"error": f"Invalid JSON or execution error: {str(e)}"})

if __name__ == "__main__":
    main()
