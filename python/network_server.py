"""
Network Server & WebSocket Live Streaming Bridge for Python Scraper:
Provides unified HTTP REST endpoints and WebSocket live streaming on 0.0.0.0:8765 using aiohttp.
Maintains the single authoritative source of truth for scraper state and disk CSV writes.
"""

import os
import sys
import json
import asyncio
import threading
import traceback
from typing import Dict, Any, Optional, List, Set

# Add python directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from aiohttp import web, WSMsgType
from services.nlp_parser import parse_search_query
from services.geo_data import get_pincodes_for_city_area
from services.csv_export import (
    ensure_csv_file_initialized,
    append_record_to_csv,
    write_all_records_to_csv,
    get_schema_columns,
    get_history_csv_files,
    load_records_from_csv_file,
    delete_history_csv_file
)
from scraper.restaurant_scraper import RestaurantScraper
from scraper.hospital_scraper import HospitalScraper
from scraper.generic_scraper import GenericScraper

from services.auth_service import auth_service

HOST = os.environ.get("SCRAPER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SCRAPER_PORT", 8765))

class ScraperStateManager:
    """Central Authoritative Scraper State."""
    def __init__(self):
        self.lock = threading.RLock()
        self.status = "idle"  # idle, starting, scraping, stopping, completed, failed
        self.search_query = ""
        self.parsed_info: Dict[str, Any] = {}
        self.pincode_queue: List[str] = []
        self.pincode_statuses: Dict[str, str] = {}
        self.current_pincode = ""
        self.pincode_index = 0
        self.pincode_total = 0
        self.current_listing_info: Optional[Dict[str, Any]] = None
        self.stats = {
            "found": 0,
            "collected": 0,
            "duplicates": 0,
            "failed": 0,
            "progress_pct": 0,
            "current_pincode": "",
            "pincode_index": 0,
            "pincode_total": 0
        }
        self.records: List[Dict[str, Any]] = []
        self.duplicates: List[Dict[str, Any]] = []
        self.output_csv_path = ""
        self.custom_fields: List[str] = []
        self.status_message = "Ready"

    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "status": self.status,
                "search_query": self.search_query,
                "parsed_info": self.parsed_info,
                "pincode_queue": list(self.pincode_queue),
                "pincode_statuses": dict(self.pincode_statuses),
                "current_pincode": self.current_pincode,
                "pincode_index": self.pincode_index,
                "pincode_total": self.pincode_total,
                "current_listing_info": self.current_listing_info,
                "stats": dict(self.stats),
                "records": list(self.records),
                "duplicates": list(self.duplicates),
                "output_csv_path": self.output_csv_path,
                "custom_fields": list(self.custom_fields),
                "status_message": self.status_message
            }

    def reset_for_new_job(self, queue: List[Dict[str, Any]], output_csv: str, custom_fields: List[str], existing_records: List[Dict[str, Any]]):
        with self.lock:
            self.status = "scraping"
            pincodes = [item.get("pincode", "") for item in queue]
            self.pincode_queue = pincodes
            self.pincode_statuses = {p: "pending" for p in pincodes}
            self.current_pincode = pincodes[0] if pincodes else ""
            self.pincode_index = 0
            self.pincode_total = len(pincodes)
            self.output_csv_path = output_csv
            self.custom_fields = list(custom_fields)
            self.records = list(existing_records)
            self.duplicates = []
            self.stats = {
                "found": 0,
                "collected": len(existing_records),
                "duplicates": 0,
                "failed": 0,
                "progress_pct": 0,
                "current_pincode": self.current_pincode,
                "pincode_index": 0,
                "pincode_total": len(pincodes)
            }
            self.current_listing_info = None
            self.status_message = f"Starting queue of {len(pincodes)} postal codes..."

state_manager = ScraperStateManager()
connected_websockets: Set[web.WebSocketResponse] = set()
ws_lock = threading.Lock()
server_loop: Optional[asyncio.AbstractEventLoop] = None
active_scraper = None
active_thread = None

def broadcast_event(event_name: str, data: Any):
    """Broadcasts a live event to all connected WebSocket clients and updates state."""
    with state_manager.lock:
        if event_name == "pincode_start":
            pin = data.get("pincode", "")
            state_manager.current_pincode = pin
            state_manager.pincode_statuses[pin] = "scraping"
            state_manager.pincode_index = data.get("index", 0)
            state_manager.pincode_total = data.get("total", len(state_manager.pincode_queue))
            state_manager.status_message = f"Scraping postal code {pin} ({state_manager.pincode_index} of {state_manager.pincode_total})..."
            if "stats" in data:
                state_manager.stats.update(data["stats"])
        elif event_name == "pincode_complete":
            pin = data.get("pincode", "")
            state_manager.pincode_statuses[pin] = "completed"
            if "stats" in data:
                state_manager.stats.update(data["stats"])
        elif event_name == "pincode_failed":
            pin = data.get("pincode", "")
            state_manager.pincode_statuses[pin] = "failed"
            if "stats" in data:
                state_manager.stats.update(data["stats"])
        elif event_name == "listing_progress":
            state_manager.current_listing_info = {
                "index": data.get("listing_index", 0),
                "total": data.get("listing_total", 0),
                "label": data.get("label", "")
            }
        elif event_name == "record":
            rec = data.get("record", {})
            state_manager.records.insert(0, rec)
            if "stats" in data:
                state_manager.stats.update(data["stats"])
        elif event_name == "duplicate":
            dup_rec = data.get("record")
            if dup_rec:
                state_manager.duplicates.insert(0, dup_rec)
            if "stats" in data:
                state_manager.stats.update(data["stats"])
        elif event_name == "progress":
            state_manager.stats.update(data)
        elif event_name == "status":
            st = data.get("status")
            if st in ["completed", "stopped", "failed"]:
                state_manager.status = st
                state_manager.status_message = f"Scraping {st}."
        elif event_name == "error":
            state_manager.status = "failed"
            state_manager.status_message = f"Error: {data.get('error', 'Unknown error')}"

    # Prepare JSON payload
    payload = json.dumps({
        "type": event_name,
        "data": data,
        "server_state": state_manager.get_state()
    })

    # Schedule sending in asyncio event loop
    if server_loop and server_loop.is_running():
        with ws_lock:
            clients = list(connected_websockets)
        for ws in clients:
            if not ws.closed:
                try:
                    asyncio.run_coroutine_threadsafe(ws.send_str(payload), server_loop)
                except Exception:
                    pass

def run_scraping_worker(
    queue: List[Dict[str, Any]],
    output_csv_path: Optional[str],
    max_results_per_pincode: int,
    existing_records: List[Dict[str, Any]],
    custom_fields: List[str]
):
    global active_scraper
    if not queue:
        broadcast_event("error", {"error": "Empty queue provided"})
        return

    first_item = queue[0]
    entity_type = (first_item.get("entity_type") or "generic").lower()

    if "school" in entity_type or "college" in entity_type or "education" in entity_type or "coaching" in entity_type:
        scraper_cls = GenericScraper
    elif "hospital" in entity_type or "clinic" in entity_type or "doctor" in entity_type or "dental" in entity_type:
        scraper_cls = HospitalScraper
    elif "restaurant" in entity_type or "cafe" in entity_type or "food" in entity_type:
        scraper_cls = RestaurantScraper
    else:
        scraper_cls = GenericScraper

    def forward_event(ev_name: str, ev_data: Any):
        broadcast_event(ev_name, ev_data)
        try:
            sys.stdout.write(json.dumps({"type": ev_name, "data": ev_data}) + "\n")
            sys.stdout.flush()
        except Exception:
            pass

    active_scraper = scraper_cls(
        event_callback=forward_event,
        headless=False,
        output_csv_path=output_csv_path,
        existing_records=existing_records,
        custom_fields=custom_fields
    )

    try:
        active_scraper.scrape_queue(
            queue=queue,
            max_results_per_pincode=max_results_per_pincode
        )
    except Exception as e:
        traceback.print_exc()
        broadcast_event("error", {"error": str(e)})
    finally:
        active_scraper = None

def _extract_token_from_request(request: web.Request) -> Optional[str]:
    """Helper to extract auth token from Authorization header, query, or custom header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    
    token_header = request.headers.get("X-Session-Token")
    if token_header:
        return token_header.strip()
        
    return request.query.get("token")

# ----------------- aiohttp CORS & Auth Middleware -----------------
@web.middleware
async def cors_and_auth_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Session-Token"
        return response

    path = request.path

    # Public endpoints that do not require authentication
    is_public = (
        path.startswith("/api/auth/") or
        path == "/api/ping"
    )

    if not is_public and path.startswith("/api/"):
        token = _extract_token_from_request(request)
        is_valid, session_info, reason = auth_service.validate_session(token)
        if not is_valid:
            resp = web.json_response({
                "error": "Unauthorized",
                "reason": reason,
                "message": "Your session has expired or is invalid. Please login again." if reason == "session_expired" else "Authentication required."
            }, status=401)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Session-Token"
            return resp
        request["user"] = session_info

    try:
        response = await handler(request)
    except web.HTTPException as ex:
        response = ex

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Session-Token"
    return response

# ----------------- Auth Handlers -----------------
async def handle_auth_login(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username:
        return web.json_response({"success": False, "error": "Username cannot be empty."}, status=400)
    if not password:
        return web.json_response({"success": False, "error": "Password cannot be empty."}, status=400)

    success, token, message = auth_service.authenticate_user(username, password)
    if not success:
        return web.json_response({"success": False, "error": message}, status=401)

    return web.json_response({
        "success": True,
        "token": token,
        "user": {
            "username": username,
            "session_timeout": auth_service.get_session_timeout()
        },
        "message": message
    })

async def handle_auth_logout(request: web.Request):
    token = _extract_token_from_request(request)
    auth_service.invalidate_session(token)
    return web.json_response({"success": True, "message": "Logged out successfully."})

async def handle_auth_verify(request: web.Request):
    token = _extract_token_from_request(request)
    is_valid, session_info, reason = auth_service.validate_session(token)
    if not is_valid:
        return web.json_response({
            "authenticated": False,
            "reason": reason,
            "message": "Your session has expired due to inactivity. Please login again." if reason == "session_expired" else "Invalid session."
        }, status=401)

    return web.json_response({
        "authenticated": True,
        "user": session_info,
        "session_timeout": auth_service.get_session_timeout()
    })

async def handle_auth_activity(request: web.Request):
    token = _extract_token_from_request(request)
    success = auth_service.record_activity(token)
    if not success:
        return web.json_response({
            "success": False,
            "reason": "session_expired",
            "message": "Your session has expired due to inactivity. Please login again."
        }, status=401)
    return web.json_response({"success": True})

async def handle_auth_verify_pin(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    pin = str(data.get("pin", "")).strip()
    if not pin:
        return web.json_response({"success": False, "error": "Enter PIN"}, status=400)

    success, reset_token, message = auth_service.verify_pin(pin)
    if not success:
        return web.json_response({"success": False, "error": message}, status=400)

    return web.json_response({
        "success": True,
        "reset_token": reset_token,
        "message": message
    })

async def handle_auth_reset_password(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    reset_token = str(data.get("reset_token", "")).strip()
    new_password = str(data.get("new_password", "")).strip()

    if not reset_token:
        return web.json_response({"success": False, "error": "Invalid or missing reset token."}, status=400)
    if not new_password:
        return web.json_response({"success": False, "error": "New password cannot be empty."}, status=400)

    success, message = auth_service.reset_password(reset_token, new_password)
    if not success:
        return web.json_response({"success": False, "error": message}, status=400)

    return web.json_response({
        "success": True,
        "message": message
    })

# ----------------- Scraper & Data Handlers -----------------
async def handle_ping(request: web.Request):
    return web.json_response({"status": "ok", "state": state_manager.get_state()})

async def handle_state(request: web.Request):
    return web.json_response(state_manager.get_state())

async def handle_parse_query(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    query = data.get("query", "")
    parsed_res = parse_search_query(query)
    with state_manager.lock:
        state_manager.search_query = query
        state_manager.parsed_info = parsed_res

    return web.json_response({
        "parsed": parsed_res,
        "suggestions": {
            "categories": [],
            "areas": [],
            "pincodes": parsed_res.get("resolved_pincodes", [])
        }
    })

async def handle_start_scraping(request: web.Request):
    global active_scraper, active_thread
    try:
        req_data = await request.json()
    except Exception:
        req_data = {}

    with state_manager.lock:
        if state_manager.status == "scraping" and active_scraper is not None:
            return web.json_response({
                "success": False,
                "error": "A scraping job is already in progress.",
                "state": state_manager.get_state()
            }, status=409)

        queue = req_data.get("queue", [])
        output_csv = req_data.get("output_csv_path") or req_data.get("target_file_path") or "export.csv"
        max_results = int(req_data.get("max_results_per_pincode", 100))
        existing_records = req_data.get("existing_records", [])
        custom_fields = req_data.get("custom_fields", [])

        state_manager.reset_for_new_job(queue, output_csv, custom_fields, existing_records)

    active_thread = threading.Thread(
        target=run_scraping_worker,
        args=(queue, output_csv, max_results, existing_records, custom_fields),
        daemon=True
    )
    active_thread.start()

    broadcast_event("status", {"status": "started", "queue_length": len(queue), "output_csv_path": output_csv})

    return web.json_response({
        "success": True,
        "status": "started",
        "state": state_manager.get_state()
    })

async def handle_stop_scraping(request: web.Request):
    global active_scraper
    if active_scraper:
        scraper_to_stop = active_scraper
        threading.Thread(target=scraper_to_stop.stop, daemon=True).start()
    with state_manager.lock:
        state_manager.status = "stopped"
        state_manager.status_message = "Scraping stopped by user."
    broadcast_event("status", {"status": "stopped"})

    return web.json_response({"success": True, "status": "stopped"})

async def handle_export_csv(request: web.Request):
    try:
        req_data = await request.json()
    except Exception:
        req_data = {}
    records = req_data.get("records", [])
    target_path = req_data.get("target_file_path") or "export.csv"
    entity_type = req_data.get("entity_type") or "business"
    custom_fields = req_data.get("custom_fields", [])
    success = write_all_records_to_csv(target_path, records, entity_type, custom_fields)
    return web.json_response({"success": success, "file_path": target_path})

async def handle_download_csv(request: web.Request):
    requested_filename = request.query.get("filename")
    csv_path = requested_filename if requested_filename else state_manager.output_csv_path
    
    if csv_path and os.path.exists(csv_path):
        filename = os.path.basename(csv_path)
        with open(csv_path, "rb") as f:
            content = f.read()
        return web.Response(
            body=content,
            content_type="text/csv",
            charset="utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    return web.json_response({"error": "CSV file not found on disk"}, status=404)

async def handle_websocket(request: web.Request):
    # Validate session token for WebSocket connection
    token = _extract_token_from_request(request)
    is_valid, _, reason = auth_service.validate_session(token)
    if not is_valid:
        # Return 401 Unauthorized for invalid WebSocket handshake
        return web.Response(
            status=401,
            text=json.dumps({"error": "Unauthorized", "reason": reason}),
            content_type="application/json"
        )

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    with ws_lock:
        connected_websockets.add(ws)

    # Immediately send full current state to newly connected client
    try:
        await ws.send_str(json.dumps({
            "type": "INIT_STATE",
            "data": state_manager.get_state()
        }))

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    action = data.get("action")
                    if action == "ping":
                        await ws.send_str(json.dumps({"type": "PONG", "data": state_manager.get_state()}))
                    elif action == "activity":
                        auth_service.record_activity(token)
                    elif action == "stop_scraping":
                        global active_scraper
                        if active_scraper:
                            threading.Thread(target=active_scraper.stop, daemon=True).start()
                        with state_manager.lock:
                            state_manager.status = "stopped"
                        broadcast_event("status", {"status": "stopped"})
                except Exception:
                    pass
            elif msg.type == WSMsgType.ERROR:
                break
    finally:
        with ws_lock:
            connected_websockets.discard(ws)

    return ws

async def handle_get_history(request: web.Request):
    files = get_history_csv_files()
    return web.json_response({"files": files, "count": len(files)})

async def handle_load_csv(request: web.Request):
    try:
        req_data = await request.json()
    except Exception:
        req_data = {}
    file_path = req_data.get("filepath") or req_data.get("filename") or ""
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
    return web.json_response(res)

async def handle_delete_csv(request: web.Request):
    try:
        req_data = await request.json()
    except Exception:
        req_data = {}
    file_path = req_data.get("filepath") or req_data.get("filename") or ""
    res = delete_history_csv_file(file_path)
    return web.json_response(res)

async def handle_get_duplicates(request: web.Request):
    with state_manager.lock:
        return web.json_response({
            "duplicates": list(state_manager.duplicates),
            "count": len(state_manager.duplicates)
        })

async def handle_clear_state(request: web.Request):
    with state_manager.lock:
        state_manager.records = []
        state_manager.duplicates = []
        state_manager.pincode_queue = []
        state_manager.pincode_statuses = {}
        state_manager.current_pincode = ""
        state_manager.pincode_index = 0
        state_manager.pincode_total = 0
        state_manager.current_listing_info = None
        state_manager.stats = {
            "found": 0,
            "collected": 0,
            "duplicates": 0,
            "failed": 0,
            "retries": 0,
            "timeout": 0,
            "progress_pct": 0,
            "current_pincode": "",
            "pincode_index": 0,
            "pincode_total": 0
        }
        state_manager.status = "idle"
        state_manager.status_message = ""
    broadcast_event("status", {
        "status": "cleared",
        "stats": state_manager.stats,
        "records": [],
        "duplicates": []
    })
    return web.json_response({"success": True})

def create_app() -> web.Application:
    app = web.Application(middlewares=[cors_and_auth_middleware])
    # Auth endpoints
    app.router.add_post("/api/auth/login", handle_auth_login)
    app.router.add_post("/api/auth/logout", handle_auth_logout)
    app.router.add_get("/api/auth/verify", handle_auth_verify)
    app.router.add_get("/api/auth/me", handle_auth_verify)
    app.router.add_post("/api/auth/activity", handle_auth_activity)
    app.router.add_post("/api/auth/verify-pin", handle_auth_verify_pin)
    app.router.add_post("/api/auth/reset-password", handle_auth_reset_password)

    # Scraper & App endpoints
    app.router.add_get("/api/ping", handle_ping)
    app.router.add_get("/api/state", handle_state)
    app.router.add_post("/api/parse_query", handle_parse_query)
    app.router.add_post("/api/start_scraping", handle_start_scraping)
    app.router.add_post("/api/stop_scraping", handle_stop_scraping)
    app.router.add_post("/api/export_csv", handle_export_csv)
    app.router.add_get("/api/download_csv", handle_download_csv)
    app.router.add_get("/api/history", handle_get_history)
    app.router.add_post("/api/load_csv", handle_load_csv)
    app.router.add_post("/api/delete_csv", handle_delete_csv)
    app.router.add_get("/api/duplicates", handle_get_duplicates)
    app.router.add_post("/api/clear_state", handle_clear_state)
    app.router.add_get("/ws", handle_websocket)
    app.router.add_get("/", handle_websocket)  # Support root ws://host:8765 as well
    return app

def start_network_bridge(host: str = HOST, port: int = PORT):
    """Starts the single unified aiohttp server on a background thread."""
    def run_server():
        global server_loop
        server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(server_loop)
        app = create_app()
        runner = web.AppRunner(app)
        server_loop.run_until_complete(runner.setup())
        try:
            site = web.TCPSite(runner, host, port)
            server_loop.run_until_complete(site.start())
            sys.stderr.write(f"[Python Network Bridge] Unified HTTP & WebSocket server running on http://{host}:{port} and ws://{host}:{port}/ws\n")
            sys.stderr.flush()
            server_loop.run_forever()
        except OSError as e:
            sys.stderr.write(f"[Python Network Bridge] Note: Port {port} is already bound/active on http://{host}:{port}\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[Python Network Bridge] Server startup exception: {e}\n")
            sys.stderr.flush()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

if __name__ == "__main__":
    print(f"[Python Network Bridge] Starting on {HOST}:{PORT}...")
    start_network_bridge(HOST, PORT)
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
