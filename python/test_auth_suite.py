"""
Auth test suite to verify:
1. Default login with Admin / Scarp@2026 succeeds
2. Bad login fails
3. Inactivity expiration
4. PIN verification and password reset
5. Login with new password succeeds and old password fails
"""

import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from services.auth_service import AuthService, auth_service, AUTH_CONFIG_FILE

def test_auth_suite():
    print("Testing AuthService...")
    test_auth = AuthService()
    
    # 1. Test Default Login
    ok, token, msg = test_auth.authenticate_user("Admin", "Scarp@2026")
    assert ok, f"Default login failed: {msg}"
    assert token is not None, "Token was not generated"
    print("[OK] Default login succeeded with Admin / Scarp@2026")
    
    # 2. Test Invalid Credentials
    ok, token_bad, msg = test_auth.authenticate_user("Admin", "WrongPassword")
    assert not ok, "Invalid password should fail"
    
    ok, token_bad, msg = test_auth.authenticate_user("WrongUser", "Scarp@2026")
    assert not ok, "Invalid username should fail"
    print("[OK] Invalid credentials correctly rejected")
    
    # 3. Test Session Validation
    is_valid, user_info, reason = test_auth.validate_session(token)
    assert is_valid, f"Session validation failed: {reason}"
    assert user_info["username"] == "Admin"
    print("[OK] Session token validated successfully")
    
    # 4. Test Inactivity Expiration
    test_auth.config["session_timeout"] = 1  # 1 second timeout for test
    time.sleep(1.2)
    is_valid, _, reason = test_auth.validate_session(token)
    assert not is_valid, "Session should have expired"
    assert reason == "session_expired"
    print("[OK] Inactivity expiration validated")
    
    # Restore normal timeout
    test_auth.config["session_timeout"] = 7200
    
    # 5. Test PIN Verification
    ok, _, msg = test_auth.verify_pin("wrong_pin")
    assert not ok, "Wrong PIN should fail"
    assert msg == "Invalid PIN"
    print("[OK] Wrong PIN correctly rejected with 'Invalid PIN'")
    
    ok, reset_token, msg = test_auth.verify_pin("123456")
    assert ok, "Valid PIN should succeed"
    assert reset_token is not None, "Reset token should be generated"
    print("[OK] Valid PIN '123456' accepted and reset token issued")
    
    # 6. Test Password Reset
    ok, msg = test_auth.reset_password(reset_token, "NewPassword@2026")
    assert ok, f"Password reset failed: {msg}"
    print("[OK] Password reset succeeded with 'NewPassword@2026'")
    
    # 7. Test Old password rejected, New password accepted
    ok, _, _ = test_auth.authenticate_user("Admin", "Scarp@2026")
    assert not ok, "Old password must be rejected"
    
    ok, new_token, msg = test_auth.authenticate_user("Admin", "NewPassword@2026")
    assert ok, "New password must be accepted"
    print("[OK] Old password rejected and new password accepted successfully")
    
    # 8. Reset back to Scarp@2026 for clean default state
    ok, reset_token, _ = test_auth.verify_pin("123456")
    test_auth.reset_password(reset_token, "Scarp@2026")
    ok, _, _ = test_auth.authenticate_user("Admin", "Scarp@2026")
    assert ok, "Reset back to default password Scarp@2026 successful"
    print("[OK] Reset back to default Scarp@2026 for clean state")
    
    print("\nALL AUTH BACKEND TESTS PASSED!")

if __name__ == "__main__":
    test_auth_suite()
