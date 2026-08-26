/**
 * Unified Scraper Bridge Service:
 * Connects React UI (both Localhost, LAN Network IP, and Electron desktop)
 * to the single shared Python Scraper process via HTTP REST & WebSocket on port 8765.
 * Attaches secure session tokens to all HTTP and WebSocket requests.
 */

import { SCRAPER_CONFIG } from '../config/scraperConfig';
import { parseClientQuery } from './nlpService';
import { authService } from '../auth/authService';

const isElectron = typeof window !== 'undefined' && window.electronAPI !== undefined;

let wsClient = null;
let wsSubscribers = new Set();
let isConnecting = false;
let reconnectTimer = null;

// Helper to attach authorization header
function getAuthHeaders(extraHeaders = {}) {
  const headers = { ...extraHeaders };
  const token = authService.getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    headers['X-Session-Token'] = token;
  }
  return headers;
}

// Check response for 401 Unauthorized / Session Expired
async function handleResponseAuth(res) {
  if (res.status === 401) {
    const data = await res.json().catch(() => ({}));
    authService.triggerSessionExpired(data.reason || 'session_expired');
    throw new Error(data.message || 'Session expired. Please login again.');
  }
  return res;
}

// Initialize WebSocket connection with automatic reconnect & auth token
export function initWebSocket() {
  if (typeof window === 'undefined') return;
  const token = authService.getToken();
  if (!token) return; // Do not open WebSocket without active authentication

  if (wsClient && (wsClient.readyState === WebSocket.OPEN || wsClient.readyState === WebSocket.CONNECTING)) {
    return;
  }

  isConnecting = true;
  const wsBase = SCRAPER_CONFIG.getWsBaseUrl();
  const wsUrl = `${wsBase}?token=${encodeURIComponent(token)}`;

  try {
    wsClient = new WebSocket(wsUrl);

    wsClient.onopen = () => {
      isConnecting = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      // Notify subscribers that connection is live
      wsSubscribers.forEach((cb) => cb({ event: 'connected', data: { ws: true } }));
    };

    wsClient.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { type, data, server_state } = payload;
        wsSubscribers.forEach((cb) => cb({ event: type, data, server_state }));
      } catch (err) {
        console.error('[ScraperBridge] WebSocket JSON parse error:', err);
      }
    };

    wsClient.onclose = (ev) => {
      isConnecting = false;
      wsSubscribers.forEach((cb) => cb({ event: 'disconnected', data: { ws: false } }));
      // If closed with auth failure or logged out, don't continually reconnect
      if (authService.getToken()) {
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(() => {
          initWebSocket();
        }, 2500);
      }
    };

    wsClient.onerror = () => {
      isConnecting = false;
      try {
        wsClient.close();
      } catch (_) {}
    };
  } catch (err) {
    isConnecting = false;
    if (authService.getToken()) {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      reconnectTimer = setTimeout(() => {
        initWebSocket();
      }, 3000);
    }
  }
}

export function closeWebSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (wsClient) {
    try {
      wsClient.close();
    } catch (_) {}
    wsClient = null;
  }
}

// Auto-start WebSocket if token exists
if (authService.getToken()) {
  initWebSocket();
}

export const ScraperBridge = {
  isAvailable: () => true, // Available everywhere (Localhost, Electron, and LAN IP!)
  isElectron: () => isElectron,
  reconnectWebSocket: () => {
    closeWebSocket();
    initWebSocket();
  },
  closeWebSocket,

  // Ping Python engine
  ping: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/ping`, {
        headers: getAuthHeaders(),
        signal: AbortSignal.timeout(3500)
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('ping');
      }
    }
    return { status: 'offline', message: 'Scraper engine not reachable' };
  },

  // Fetch full authoritative server state
  getState: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/state`, {
        headers: getAuthHeaders(),
        signal: AbortSignal.timeout(3500)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('[ScraperBridge] Could not fetch server state over HTTP:', e);
    }
    return null;
  },

  // Parse natural language search query
  parseQuery: async (query) => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/parse_query`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ query }),
        signal: AbortSignal.timeout(3000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      // Fallback to client-side NLP parser for instantaneous typing responsiveness
    }

    const parsed = parseClientQuery(query);
    return {
      parsed,
      suggestions: {
        categories: [],
        areas: [],
        pincodes: parsed.resolved_pincodes || []
      }
    };
  },

  // Select save file location natively (or generate default path for LAN browser)
  showSaveDialog: async (defaultFilename) => {
    if (isElectron) {
      return await window.electronAPI.showSaveDialog(defaultFilename);
    }
    return { canceled: false, filePath: defaultFilename || 'export.csv' };
  },

  // Start sequential pincode queue scraping (Unified Python Backend)
  startScraping: async ({ queue, outputCsvPath, maxResultsPerPincode = 100, existingRecords = [], customFields = [] }) => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/start_scraping`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          queue,
          output_csv_path: outputCsvPath,
          max_results_per_pincode: maxResultsPerPincode,
          existing_records: existingRecords,
          custom_fields: customFields
        })
      });

      await handleResponseAuth(res);

      if (res.status === 409) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || 'A scraping job is already running on the server.');
      }

      if (res.ok) {
        return await res.json();
      }
      const errText = await res.text().catch(() => '');
      throw new Error(errText || `Server returned error (${res.status})`);
    } catch (err) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('start_scraping', {
          queue,
          output_csv_path: outputCsvPath,
          max_results_per_pincode: maxResultsPerPincode,
          existing_records: existingRecords,
          custom_fields: customFields
        });
      }
      if (err.message && (err.message.includes('offline') || err.message.includes('running') || err.message.includes('Session expired'))) {
        throw err;
      }
      throw new Error(`Scraper Engine offline on ${SCRAPER_CONFIG.getHttpBaseUrl()}. Please restart with "npm run dev".`);
    }
  },

  // Stop scraping on the shared Python process
  stopScraping: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/stop_scraping`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({})
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('stop_scraping');
      }
    }
    return { status: 'stopped' };
  },

  // Export CSV (Saves on host disk and triggers browser download for LAN clients)
  exportCsv: async (records, defaultFilename, entityType = 'business', customFields = []) => {
    const filename = defaultFilename || 'export.csv';

    // 1. If in Electron, save natively to chosen path
    if (isElectron) {
      const saveResult = await window.electronAPI.showSaveDialog(filename);
      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, canceled: true };
      }
      return await window.electronAPI.sendToPython('export_csv', {
        records,
        target_file_path: saveResult.filePath,
        entity_type: entityType,
        custom_fields: customFields
      });
    }

    // 2. If in LAN Network Browser, trigger direct HTTP file download from Python host
    try {
      // First, tell the server to save the current in-memory records to the file
      const exportRes = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/export_csv`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          records,
          target_file_path: filename,
          entity_type: entityType,
          custom_fields: customFields
        }),
        signal: AbortSignal.timeout(10000)
      });
      await handleResponseAuth(exportRes);
      
      let finalPath = filename;
      if (exportRes.ok) {
        const jsonRes = await exportRes.json();
        if (jsonRes.file_path) {
          finalPath = jsonRes.file_path;
        }
      }

      // Now trigger the download with auth token in query
      const token = authService.getToken();
      const downloadUrl = `${SCRAPER_CONFIG.getHttpBaseUrl()}/api/download_csv?filename=${encodeURIComponent(finalPath)}&token=${encodeURIComponent(token || '')}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', finalPath.split(/[\\/]/).pop());
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return { success: true, file_path: finalPath };
    } catch (e) {
      // Fallback to client-side CSV blob download if server is unreachable
      const headers = Object.keys(records[0] || {}).join(',');
      const rows = records.map((r) => Object.values(r).map((v) => `"${String(v || '').replace(/"/g, '""')}"`).join(','));
      const csvBlob = new Blob(['\uFEFF' + [headers, ...rows].join('\n')], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(csvBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return { success: true, file_path: filename };
    }
  },

  // Fetch list of saved historical CSV files
  getHistory: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/history`, {
        headers: getAuthHeaders(),
        signal: AbortSignal.timeout(4000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('get_history');
      }
    }
    return { files: [], count: 0 };
  },

  // Load a historical CSV file directly into active table dataset
  loadCsv: async (filePathOrName) => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/load_csv`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ filepath: filePathOrName }),
        signal: AbortSignal.timeout(8000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('load_csv', { filepath: filePathOrName });
      }
    }
    return { success: false, error: 'Could not load CSV file from engine.' };
  },

  // Delete a historical CSV file
  deleteCsv: async (filePathOrName) => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/delete_csv`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ filepath: filePathOrName }),
        signal: AbortSignal.timeout(4000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('delete_csv', { filepath: filePathOrName });
      }
    }
    return { success: false, error: 'Could not delete CSV file.' };
  },

  // Fetch duplicates log
  getDuplicates: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/duplicates`, {
        headers: getAuthHeaders(),
        signal: AbortSignal.timeout(3000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {}
    return { duplicates: [], count: 0 };
  },

  // Clear server state
  clearState: async () => {
    try {
      const res = await fetch(`${SCRAPER_CONFIG.getHttpBaseUrl()}/api/clear_state`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        signal: AbortSignal.timeout(3000)
      });
      await handleResponseAuth(res);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      if (isElectron) {
        return await window.electronAPI.sendToPython('clear_state');
      }
    }
    return { success: false };
  },

  // Listen to live events from Python via WebSocket & Electron IPC
  onScraperEvent: (callback) => {
    wsSubscribers.add(callback);
    initWebSocket();

    let unsubscribeElectron = null;
    if (isElectron) {
      unsubscribeElectron = window.electronAPI.onPythonEvent(callback);
    }

    return () => {
      wsSubscribers.delete(callback);
      if (typeof unsubscribeElectron === 'function') {
        unsubscribeElectron();
      }
    };
  },

  // Intercept app closing (Electron only)
  onAppClosing: (callback) => {
    if (!isElectron) return;
    window.electronAPI.onAppClosing(callback);
  },

  respondToClosing: (shouldClose) => {
    if (!isElectron) return;
    window.electronAPI.respondToClosing(shouldClose);
  }
};

export default ScraperBridge;
