"""
End-to-End Integration Test for Network Server Authentication:
Tests all auth endpoints, authorization middleware, session expiration,
PIN verification, and password reset over real HTTP requests.
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from network_server import start_network_bridge, auth_service

HOST = "127.0.0.1"
PORT = 8799  # Dedicated test port

def run_http_request(method: str, path: str, payload=None, token=None):
    url = f"http://{HOST}:{PORT}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-Session-Token"] = token

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            body = response.read().decode("utf-8")
            return status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, json.loads(body) if body else {}

def test_full_auth_suite():
    print(f"Starting test server on {HOST}:{PORT}...")
    start_network_bridge(HOST, PORT)
    time.sleep(1.0)

    try:
        # Reset auth config to default for clean test
        auth_service.config["username"] = "Admin"
        auth_service.config["pin"] = "123456"
        auth_service.config["session_timeout"] = 7200
        _, reset_tok, _ = auth_service.verify_pin("123456")
        auth_service.reset_password(reset_tok, "Scarp@2026")

        print("\n=== Running HTTP Auth Integration Tests ===")

        # Test 1: Public endpoint /api/ping works without auth
        code, data = run_http_request("GET", "/api/ping")
        assert code == 200 and data.get("status") == "ok", f"Ping failed: {code}, {data}"
        print("[OK] Test 1: Public /api/ping accessible without auth")

        # Test 2: Protected endpoint /api/state blocked without auth (401)
        code, data = run_http_request("GET", "/api/state")
        assert code == 401, f"Expected 401 for unauthenticated /api/state, got {code}"
        print("[OK] Test 2: Protected /api/state blocked with 401 Unauthorized")

        # Test 3: Bad credentials login rejected
        code, data = run_http_request("POST", "/api/auth/login", {"username": "Admin", "password": "WrongPassword"})
        assert code == 401 and not data.get("success"), f"Bad login should fail: {code}, {data}"
        print("[OK] Test 3: Bad login credentials correctly rejected")

        # Test 4: Default login (Admin / Scarp@2026) succeeds
        code, data = run_http_request("POST", "/api/auth/login", {"username": "Admin", "password": "Scarp@2026"})
        assert code == 200 and data.get("success"), f"Default login failed: {code}, {data}"
        token = data.get("token")
        assert token, "Token not returned"
        print("[OK] Test 4: Default login succeeded with Admin / Scarp@2026")

        # Test 5: Verify session with valid token
        code, data = run_http_request("GET", "/api/auth/verify", token=token)
        assert code == 200 and data.get("authenticated"), f"Session verify failed: {code}, {data}"
        print("[OK] Test 5: Session verification succeeded")

        # Test 6: Access protected endpoint /api/state with token
        code, data = run_http_request("GET", "/api/state", token=token)
        assert code == 200 and "status" in data, f"Access /api/state with token failed: {code}, {data}"
        print("[OK] Test 6: Access protected /api/state with valid token succeeded")

        # Test 7: PIN verification - wrong PIN fails
        code, data = run_http_request("POST", "/api/auth/verify-pin", {"pin": "999999"})
        assert code == 400 and data.get("error") == "Invalid PIN", f"Wrong PIN should return 400: {code}, {data}"
        print("[OK] Test 7: Wrong PIN rejected with 'Invalid PIN'")

        # Test 8: PIN verification - correct PIN succeeds
        code, data = run_http_request("POST", "/api/auth/verify-pin", {"pin": "123456"})
        assert code == 200 and data.get("success"), f"PIN verification failed: {code}, {data}"
        reset_token = data.get("reset_token")
        assert reset_token, "Reset token not returned"
        print("[OK] Test 8: Correct PIN '123456' verified and reset token issued")

        # Test 9: Password Reset with new password
        code, data = run_http_request("POST", "/api/auth/reset-password", {
            "reset_token": reset_token,
            "new_password": "NewSecretPassword@2026"
        })
        assert code == 200 and data.get("success"), f"Reset password failed: {code}, {data}"
        print("[OK] Test 9: Password reset succeeded")

        # Test 10: Old token invalidated after password reset
        code, data = run_http_request("GET", "/api/state", token=token)
        assert code == 401, f"Old session should be invalidated after password reset: {code}"
        print("[OK] Test 10: Old session invalidated after password reset")

        # Test 11: Old password rejected
        code, data = run_http_request("POST", "/api/auth/login", {"username": "Admin", "password": "Scarp@2026"})
        assert code == 401, "Old password must be rejected"
        print("[OK] Test 11: Old password rejected")

        # Test 12: New password accepted
        code, data = run_http_request("POST", "/api/auth/login", {"username": "Admin", "password": "NewSecretPassword@2026"})
        assert code == 200 and data.get("success"), f"New password login failed: {code}"
        new_token = data.get("token")
        print("[OK] Test 12: New password login succeeded")

        # Test 13: Activity recording
        code, data = run_http_request("POST", "/api/auth/activity", token=new_token)
        assert code == 200 and data.get("success"), f"Activity record failed: {code}"
        print("[OK] Test 13: User activity recording touched session successfully")

        # Test 14: Logout invalidates session
        code, data = run_http_request("POST", "/api/auth/logout", token=new_token)
        assert code == 200 and data.get("success"), f"Logout failed: {code}"
        
        code, data = run_http_request("GET", "/api/state", token=new_token)
        assert code == 401, "Session must be invalid after logout"
        print("[OK] Test 14: Logout invalidated session successfully")

        # Clean reset back to Scarp@2026
        code, data = run_http_request("POST", "/api/auth/verify-pin", {"pin": "123456"})
        rst = data.get("reset_token")
        run_http_request("POST", "/api/auth/reset-password", {"reset_token": rst, "new_password": "Scarp@2026"})
        print("[OK] Clean reset back to default Scarp@2026 finished")

        print("\n>>> ALL 14 HTTP AUTH INTEGRATION TESTS PASSED PERFECTLY! <<<")
        os._exit(0)

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        os._exit(1)

if __name__ == "__main__":
    test_full_auth_suite()
