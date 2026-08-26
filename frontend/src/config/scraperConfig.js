/**
 * Central Scraper Configuration:
 * Automatically resolves the host address whether opened via localhost or LAN network IP (e.g. 192.168.1.13).
 */

const getHost = () => {
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const hostname = window.location.hostname;
    // If opened via local file or empty, default to localhost
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
    const port = SCRAPER_CONFIG.PORT;
    return `http://${host}:${port}`;
  },
  getWsBaseUrl: () => {
    const host = getHost();
    const port = SCRAPER_CONFIG.PORT;
    return `ws://${host}:${port}/ws`;
  }
};
