/**
 * Inactivity Timer Hook:
 * Enforces a 2-hour (7200s) automatic logout based on user inactivity.
 * Detects user interaction (mouse move, clicks, keyboard, scroll, touch) and
 * sends throttled activity heartbeat to the backend.
 */

import { useEffect, useRef, useCallback } from 'react';
import { authService } from './authService';

const DEFAULT_TIMEOUT_SECONDS = 7200; // 2 hours
const THROTTLE_ACTIVITY_MS = 30000; // Notify backend at most once every 30s

export function useInactivityTimer({
  isAuthenticated,
  timeoutSeconds = DEFAULT_TIMEOUT_SECONDS,
  onSessionExpired
}) {
  const timerRef = useRef(null);
  const lastBackendPingRef = useRef(0);

  const handleTimeout = useCallback(() => {
    console.warn('[Auth] Inactivity timeout reached (2 hours). Logging out...');
    authService.logout();
    if (typeof onSessionExpired === 'function') {
      onSessionExpired('Your session has expired due to inactivity. Please login again.');
    }
  }, [onSessionExpired]);

  const resetTimer = useCallback(() => {
    if (!isAuthenticated) return;

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(handleTimeout, timeoutSeconds * 1000);

    // Throttled notification to backend
    const now = Date.now();
    if (now - lastBackendPingRef.current > THROTTLE_ACTIVITY_MS) {
      lastBackendPingRef.current = now;
      authService.recordActivity().catch(() => {});
    }
  }, [isAuthenticated, timeoutSeconds, handleTimeout]);

  useEffect(() => {
    if (!isAuthenticated) {
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    // Set initial timeout
    resetTimer();

    // Interaction event listeners
    const events = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    const handleActivity = () => {
      resetTimer();
    };

    events.forEach((eventName) => {
      window.addEventListener(eventName, handleActivity, { passive: true });
    });

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      events.forEach((eventName) => {
        window.removeEventListener(eventName, handleActivity);
      });
    };
  }, [isAuthenticated, resetTimer]);

  return { resetTimer };
}

export default useInactivityTimer;
