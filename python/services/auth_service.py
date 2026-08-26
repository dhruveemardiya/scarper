"""
Authentication and Session Management Service:
Provides zero-database server-side credential verification, secure password hashing,
PIN-based password reset, and user-inactivity session lifecycle management.
"""

import os
import json
import time
import secrets
import hashlib
import hmac
import threading
from typing import Dict, Any, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
AUTH_CONFIG_FILE = os.path.join(DATA_DIR, "auth_config.json")

# Default credentials and configuration
DEFAULT_USERNAME = os.environ.get("AUTH_USERNAME", "Admin")
DEFAULT_PASSWORD = os.environ.get("AUTH_PASSWORD", "Scarp@2026")
DEFAULT_PIN = os.environ.get("FORGOT_PASSWORD_PIN", "123456")
DEFAULT_SESSION_TIMEOUT = int(os.environ.get("SESSION_TIMEOUT", 7200))  # 2 hours in seconds

def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password with PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    )
    return key.hex(), salt

def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a password against the stored PBKDF2 hash."""
    computed_hash, _ = _hash_password(password, salt)
    return hmac.compare_digest(computed_hash, stored_hash)


class AuthService:
    """
    Manages server-side authentication, credentials persistence (in data/auth_config.json),
    active session tracking with 2-hour inactivity expiration, and PIN-based password reset.
    """
    def __init__(self):
        self.lock = threading.RLock()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.reset_tokens: Dict[str, Dict[str, Any]] = {}
        self._ensure_data_dir()
        self._load_or_init_config()

    def _ensure_data_dir(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _load_or_init_config(self):
        """Loads existing configuration or initializes with defaults."""
        with self.lock:
            if os.path.exists(AUTH_CONFIG_FILE):
                try:
                    with open(AUTH_CONFIG_FILE, "r", encoding="utf-8") as f:
                        self.config = json.load(f)
                    # Verify required keys exist
                    if "username" in self.config and "password_hash" in self.config and "salt" in self.config:
                        # Allow env overrides for timeout / pin if provided
                        if "FORGOT_PASSWORD_PIN" in os.environ:
                            self.config["pin"] = os.environ["FORGOT_PASSWORD_PIN"]
                        if "SESSION_TIMEOUT" in os.environ:
                            self.config["session_timeout"] = int(os.environ["SESSION_TIMEOUT"])
                        return
                except Exception as e:
                    print(f"[AuthService] Error reading auth config, reinitializing defaults: {e}")

            # Initialize with default credentials
            pwd_hash, salt = _hash_password(DEFAULT_PASSWORD)
            self.config = {
                "username": DEFAULT_USERNAME,
                "password_hash": pwd_hash,
                "salt": salt,
                "pin": DEFAULT_PIN,
                "session_timeout": DEFAULT_SESSION_TIMEOUT,
                "updated_at": time.time()
            }
            self._save_config()

    def _save_config(self):
        """Persists current auth configuration to disk."""
        with self.lock:
            try:
                with open(AUTH_CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2)
            except Exception as e:
                print(f"[AuthService] Error writing auth config to disk: {e}")

    def get_session_timeout(self) -> int:
        """Returns the configured session inactivity timeout in seconds."""
        with self.lock:
            return int(self.config.get("session_timeout", DEFAULT_SESSION_TIMEOUT))

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[str], str]:
        """
        Validates username and password against server configuration.
        Returns (success, session_token, message).
        """
        with self.lock:
            self._load_or_init_config()
            if not username or not password:
                return False, None, "Username and password are required."

            stored_user = self.config.get("username", DEFAULT_USERNAME)
            stored_hash = self.config.get("password_hash", "")
            salt = self.config.get("salt", "")

            # Case-sensitive username check or standard match
            if username.strip().lower() != stored_user.lower():
                return False, None, "Invalid username or password."

            if not _verify_password(password, stored_hash, salt):
                return False, None, "Invalid username or password."

            # Credentials valid - create active session
            token = self._create_session(stored_user)
            return True, token, "Authentication successful."

    def _create_session(self, username: str) -> str:
        """Creates a cryptographically secure session token."""
        token = secrets.token_hex(32)
        now = time.time()
        with self.lock:
            self.sessions[token] = {
                "token": token,
                "username": username,
                "created_at": now,
                "last_active_at": now
            }
            self._cleanup_expired_sessions()
        return token

    def validate_session(self, token: Optional[str]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validates an active session token and checks for inactivity expiration (2 hours).
        Returns (is_valid, session_data, reason).
        """
        if not token:
            return False, None, "missing_token"

        now = time.time()
        timeout = self.get_session_timeout()

        with self.lock:
            session = self.sessions.get(token)
            if not session:
                return False, None, "invalid_session"

            last_active = session.get("last_active_at", 0)
            if now - last_active > timeout:
                # Session expired due to inactivity
                del self.sessions[token]
                return False, None, "session_expired"

            # Session is valid - update last_active_at
            session["last_active_at"] = now
            return True, {
                "username": session["username"],
                "created_at": session["created_at"],
                "last_active_at": session["last_active_at"],
                "expires_in": int(timeout - (now - session["last_active_at"]))
            }, "ok"

    def record_activity(self, token: Optional[str]) -> bool:
        """Touches the session to reset the inactivity timer."""
        if not token:
            return False
        with self.lock:
            session = self.sessions.get(token)
            if not session:
                return False
            now = time.time()
            timeout = self.get_session_timeout()
            if now - session.get("last_active_at", 0) > timeout:
                del self.sessions[token]
                return False
            session["last_active_at"] = now
            return True

    def invalidate_session(self, token: Optional[str]) -> bool:
        """Destroys an active session (Logout)."""
        if not token:
            return False
        with self.lock:
            if token in self.sessions:
                del self.sessions[token]
                return True
            return False

    def verify_pin(self, entered_pin: str) -> Tuple[bool, Optional[str], str]:
        """
        Validates security PIN against backend configuration.
        On success, returns (True, reset_token, "PIN verified successfully.").
        """
        with self.lock:
            self._load_or_init_config()
            if not entered_pin:
                return False, None, "Security PIN is required."

            configured_pin = str(self.config.get("pin", DEFAULT_PIN)).strip()
            if entered_pin.strip() != configured_pin:
                return False, None, "Invalid PIN"

            # Create a 5-minute single-use reset token
            reset_token = secrets.token_hex(24)
            self.reset_tokens[reset_token] = {
                "created_at": time.time(),
                "expires_at": time.time() + 300  # 5 minutes
            }
            return True, reset_token, "PIN verified successfully."

    def reset_password(self, reset_token: str, new_password: str) -> Tuple[bool, str]:
        """
        Sets a new password using a verified reset token.
        Validates password rules and persists the change to server configuration.
        """
        if not reset_token or not new_password:
            return False, "Reset token and new password are required."

        if len(new_password) < 6:
            return False, "Password must be at least 6 characters long."

        now = time.time()
        with self.lock:
            token_data = self.reset_tokens.get(reset_token)
            if not token_data or now > token_data.get("expires_at", 0):
                if reset_token in self.reset_tokens:
                    del self.reset_tokens[reset_token]
                return False, "Password reset session has expired or is invalid. Please verify PIN again."

            # Consume the reset token
            del self.reset_tokens[reset_token]

            # Hash new password and save
            pwd_hash, salt = _hash_password(new_password)
            self.config["password_hash"] = pwd_hash
            self.config["salt"] = salt
            self.config["updated_at"] = now
            self._save_config()

            # Invalidate all current active sessions to force re-login with new password
            self.sessions.clear()

            return True, "Password changed successfully. Please login with your new password."

    def _cleanup_expired_sessions(self):
        """Cleans up inactive sessions and expired reset tokens."""
        now = time.time()
        timeout = self.get_session_timeout()
        expired_tokens = [
            t for t, s in self.sessions.items()
            if now - s.get("last_active_at", 0) > timeout
        ]
        for t in expired_tokens:
            del self.sessions[t]

        expired_resets = [
            t for t, r in self.reset_tokens.items()
            if now > r.get("expires_at", 0)
        ]
        for t in expired_resets:
            del self.reset_tokens[t]


# Singleton instance
auth_service = AuthService()
