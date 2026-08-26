/**
 * Frontend Authentication Service:
 * Handles secure communication with the backend authentication endpoints.
 * Never stores or validates plain-text passwords or PINs on the client.
 */

import { SCRAPER_CONFIG } from '../config/scraperConfig';

const SESSION_TOKEN_KEY = 'scraper_session_token';

let inMemoryToken = null;
let onSessionExpiredCallback = null;

export const authService = {
  /**
   * Sets a callback to be triggered when a session expiration is detected.
   */
  setSessionExpiredHandler: (callback) => {
    onSessionExpiredCallback = callback;
  },

  /**
   * Triggers session expiration handler if registered.
   */
  triggerSessionExpired: (reason = 'session_expired') => {
    authService.clearToken();
    if (typeof onSessionExpiredCallback === 'function') {
      onSessionExpiredCallback(reason);
    }
  },

  /**
   * Retrieves the current session token (memory or sessionStorage for refresh persistence).
   */
  getToken: () => {
    if (inMemoryToken) return inMemoryToken;
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        const stored = window.sessionStorage.getItem(SESSION_TOKEN_KEY);
        if (stored) {
          inMemoryToken = stored;
          return stored;
        }
      } catch (_) {}
    }
    return null;
  },

  /**
   * Stores the session token.
   */
  setToken: (token) => {
    inMemoryToken = token;
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        if (token) {
          window.sessionStorage.setItem(SESSION_TOKEN_KEY, token);
        } else {
          window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
        }
      } catch (_) {}
    }
  },

  /**
   * Clears the active session token.
   */
  clearToken: () => {
    inMemoryToken = null;
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
      } catch (_) {}
    }
  },

  /**
   * Authenticates user against backend configuration.
   */
  login: async (username, password) => {
    const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        return {
          success: false,
          error: data.error || 'Invalid username or password.'
        };
      }

      authService.setToken(data.token);
      return {
        success: true,
        token: data.token,
        user: data.user,
        message: data.message
      };
    } catch (err) {
      return {
        success: false,
        error: 'Unable to connect to backend server. Please make sure the server is running.'
      };
    }
  },

  /**
   * Verifies current session token with the backend.
   */
  verifySession: async () => {
    const token = authService.getToken();
    if (!token) {
      return { authenticated: false, reason: 'no_token' };
    }

    const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/api/auth/verify`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await res.json();
      if (!res.ok || !data.authenticated) {
        authService.clearToken();
        return {
          authenticated: false,
          reason: data.reason || 'session_expired',
          message: data.message || 'Session expired.'
        };
      }

      return {
        authenticated: true,
        user: data.user,
        sessionTimeout: data.session_timeout || 7200
      };
    } catch (err) {
      // If server unreachable, retain token or report error
      return { authenticated: false, reason: 'network_error', message: 'Backend unreachable.' };
    }
  },

  /**
   * Notifies backend of user interaction to reset inactivity timer.
   */
  recordActivity: async () => {
    const token = authService.getToken();
    if (!token) return false;

    const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/api/auth/activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.status === 401) {
        authService.triggerSessionExpired('session_expired');
        return false;
      }
      return res.ok;
    } catch (_) {
      return false;
    }
  },

  /**
   * Verifies Security PIN on the backend for password reset.
   */
  verifyPin: async (pin) => {
    const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/api/auth/verify-pin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        return {
          success: false,
          error: data.error || 'Invalid PIN'
        };
      }

      return {
        success: true,
        resetToken: data.reset_token,
        message: data.message
      };
    } catch (err) {
      return {
        success: false,
        error: 'Server error while verifying PIN.'
      };
    }
  },

  /**
   * Sets a new password via backend reset endpoint using verified reset token.
   */
  resetPassword: async (resetToken, newPassword) => {
    const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reset_token: resetToken,
          new_password: newPassword
        })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        return {
          success: false,
          error: data.error || 'Failed to reset password.'
        };
      }

      return {
        success: true,
        message: data.message || 'Password changed successfully. Please login with your new password.'
      };
    } catch (err) {
      return {
        success: false,
        error: 'Server error while updating password.'
      };
    }
  },

  /**
   * Logs out user and invalidates server-side session.
   */
  logout: async () => {
    const token = authService.getToken();
    if (token) {
      const baseUrl = SCRAPER_CONFIG.getHttpBaseUrl();
      try {
        await fetch(`${baseUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (_) {}
    }
    authService.clearToken();
  }
};

export default authService;
