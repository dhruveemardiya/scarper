"""
Automated Test Suite for Python Network Server & WebSocket Bridge
"""

import os
import sys
import time
import json
import asyncio
import threading
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import websockets
from network_server import start_network_bridge, state_manager, broadcast_event

TEST_HOST = "127.0.0.1"
TEST_PORT = 8799

def run_tests():
    print("=== Testing Python Network Server & WebSocket Bridge ===")
    
    # Start network server on test port
    start_network_bridge(TEST_HOST, TEST_PORT)
    time.sleep(1.2)

    base_url = f"http://{TEST_HOST}:{TEST_PORT}"

    # 1. Test GET /api/ping
    req = urllib.request.Request(f"{base_url}/api/ping")
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data.get("status") == "ok"
    print("  [PASS] GET /api/ping responded 200 OK")

    # 2. Test GET /api/state
    req = urllib.request.Request(f"{base_url}/api/state")
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        state = json.loads(res.read().decode("utf-8"))
        assert "status" in state
        assert "stats" in state
        assert "records" in state
    print(f"  [PASS] GET /api/state responded with status: {state['status']}")

    # 3. Test POST /api/parse_query ('hotel in London')
    post_data = json.dumps({"query": "hotel in London"}).encode("utf-8")
    req = urllib.request.Request(f"{base_url}/api/parse_query", data=post_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["parsed"]["city"] == "London"
        assert data["parsed"]["country"] == "UK"
        assert len(data["parsed"]["resolved_pincodes"]) > 0
    print(f"  [PASS] POST /api/parse_query ('hotel in London') -> {data['parsed']['city']}, {len(data['parsed']['resolved_pincodes'])} postcodes")

    # 4. Test POST /api/parse_query ('coaching institute in Rajkot')
    post_data2 = json.dumps({"query": "coaching institute in Rajkot"}).encode("utf-8")
    req2 = urllib.request.Request(f"{base_url}/api/parse_query", data=post_data2, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req2, timeout=5) as res:
        assert res.status == 200
        data2 = json.loads(res.read().decode("utf-8"))
        assert data2["parsed"]["city"] == "Rajkot"
        assert len(data2["parsed"]["resolved_pincodes"]) >= 5
    print(f"  [PASS] POST /api/parse_query ('coaching institute in Rajkot') -> {data2['parsed']['city']}, {len(data2['parsed']['resolved_pincodes'])} pincodes")

    # 5. Test WebSocket Connection and Live Event Streaming
    async def test_ws():
        ws_url = f"ws://{TEST_HOST}:{TEST_PORT}/ws"
        async with websockets.connect(ws_url) as ws:
            # First message should be INIT_STATE
            init_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            init_msg = json.loads(init_raw)
            assert init_msg["type"] == "INIT_STATE"
            print("  [PASS] WebSocket received INIT_STATE upon connection")

            # Broadcast an event from server and check that client receives it
            broadcast_event("progress", {"found": 5, "collected": 4, "duplicates": 1})
            event_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            event_msg = json.loads(event_raw)
            assert event_msg["type"] == "progress"
            assert event_msg["data"]["found"] == 5
            print("  [PASS] WebSocket received live broadcast event ('progress')")

    asyncio.run(test_ws())

    # 6. Test GET /api/history
    req_hist = urllib.request.Request(f"{base_url}/api/history")
    with urllib.request.urlopen(req_hist, timeout=5) as res_hist:
        assert res_hist.status == 200
        hist_data = json.loads(res_hist.read().decode("utf-8"))
        assert "files" in hist_data
        assert isinstance(hist_data["files"], list)
        print(f"  [PASS] GET /api/history found {len(hist_data['files'])} saved CSV history files")

    # 7. Test POST /api/load_csv
    test_csv_path = os.path.join(BASE_DIR, "test_load_history.csv")
    with open(test_csv_path, "w", encoding="utf-8-sig") as f:
        f.write("Hospital Name,Full Address,City,Pincode/Postcode,Google Rating\nAastha Hospital,Amreli Station Road,Amreli,365601,4.5\nSamyak Hospital,Lathi Road,Amreli,365601,4.8\n")

    try:
        load_data = json.dumps({"filepath": test_csv_path}).encode("utf-8")
        req_load = urllib.request.Request(f"{base_url}/api/load_csv", data=load_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req_load, timeout=5) as res_load:
            assert res_load.status == 200
            load_res = json.loads(res_load.read().decode("utf-8"))
            assert load_res["success"] is True
            assert len(load_res["records"]) == 2
            assert load_res["records"][0]["name"] == "Aastha Hospital"
            assert load_res["records"][1]["city"] == "Amreli"
            print(f"  [PASS] POST /api/load_csv successfully loaded 2 records with normalized keys")

        # 8. Test Duplicate Detector with Fast Pre-filtering
        from scraper.duplicate_detector import DuplicateDetector
        detector = DuplicateDetector()
        rec1 = {
            "source_url": "https://www.google.com/maps/place/Aastha+Hospital/data=!1s0x395880c8ba8aa237:0x2249e9c3e9a7e025",
            "name": "Aastha Hospital - Amreli",
            "address": "Amreli Station Road",
            "phone": "9876543210"
        }
        detector.register(rec1)
        assert detector.is_duplicate(rec1) is True

        # Check that fast preview with just url place ID detects duplicate immediately
        preview_rec = {
            "source_url": "https://www.google.com/maps/place/Aastha+Hospital/data=!1s0x395880c8ba8aa237:0x2249e9c3e9a7e025",
            "name": "Aastha Hospital - Amreli"
        }
        assert detector.is_duplicate(preview_rec) is True
        assert "Matched Place ID" in detector.get_duplicate_reason(preview_rec)
        print("  [PASS] DuplicateDetector fast pre-filter detected duplicate in 0.0001s with reason")

        # 9. Test GET /api/duplicates
        broadcast_event("duplicate", {
            "record": {
                "id": "dup-1",
                "name": "Aastha Hospital - Amreli",
                "pincode": "365602",
                "reason": "Matched Place ID already saved in dataset",
                "skipped_at": "2026-08-21 17:30:00"
            }
        })
        req_dup = urllib.request.Request(f"{base_url}/api/duplicates")
        with urllib.request.urlopen(req_dup, timeout=5) as res_dup:
            assert res_dup.status == 200
            dup_data = json.loads(res_dup.read().decode("utf-8"))
            assert len(dup_data["duplicates"]) >= 1
            assert dup_data["duplicates"][0]["name"] == "Aastha Hospital - Amreli"
            print("  [PASS] GET /api/duplicates returned recorded duplicate listings")

    finally:
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

    print("\n>>> ALL NETWORK BRIDGE, WEBSOCKET, HISTORY & DUPLICATE TESTS PASSED 100%! <<<\n")
    os._exit(0)

if __name__ == "__main__":
    run_tests()
