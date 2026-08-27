/**
 * Central Scraper Configuration:
 * Automatically resolves the host address whether opened via localhost, LAN network IP,
 * or production (Vercel frontend + Render backend on different domains).
 */

const RENDER_BACKEND_HOST = 'scarper-6jf7.onrender.com';

const isProduction = () => {
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const hostname = window.location.hostname;
    return hostname.endsWith('.vercel.app') || hostname === RENDER_BACKEND_HOST;
  }
  return false;
};

const getHost = () => {
  if (isProduction()) {
    return RENDER_BACKEND_HOST;
  }
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const hostname = window.location.hostname;
    if (hostname === '' || hostname === 'about:blank') {
      return '127.0.0.1';
    }
    return hostname;
  }
  return '127.0.0.1';
};

export const SCRAPER_CONFIG = {
  PORT: 8765,
  getHost,
  getHttpBaseUrl: () => {
    const host = getHost();
    if (isProduction()) {
      return `https://${host}`;
    }
    const port = SCRAPER_CONFIG.PORT;
    return `http://${host}:${port}`;
  },
  getWsBaseUrl: () => {
    const host = getHost();
    if (isProduction()) {
      return `wss://${host}/ws`;
    }
    const port = SCRAPER_CONFIG.PORT;
    return `ws://${host}:${port}/ws`;
  }
};