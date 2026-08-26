const { spawn } = require('child_process');
const path = require('path');
const readline = require('readline');

class PythonBridge {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.process = null;
    this.pendingRequests = new Map();
    this.requestIdCounter = 1;
    this.isReady = false;
  }

  start() {
    const pythonScript = path.join(__dirname, '..', 'python', 'run_scraper.py');
    const pythonCwd = path.join(__dirname, '..', 'python');

    // Spawn python in unbuffered mode (-u)
    this.process = spawn('python', ['-u', pythonScript], {
      cwd: pythonCwd,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    const rl = readline.createInterface({
      input: this.process.stdout,
      terminal: false
    });

    rl.on('line', (line) => {
      const trimmed = line ? line.trim() : '';
      if (!trimmed) return;
      if (!trimmed.startsWith('{')) {
        console.log('[Python Log]:', trimmed);
        return;
      }
      try {
        const message = JSON.parse(trimmed);
        this.handleMessage(message);
      } catch (err) {
        console.error('[PythonBridge] JSON parse error:', err, 'Raw line:', line);
      }
    });

    this.process.stderr.on('data', (data) => {
      console.error('[PythonBridge Stderr]:', data.toString());
    });

    this.process.on('close', (code) => {
      console.log(`[PythonBridge] Python process exited with code ${code}`);
      this.isReady = false;
    });

    this.process.on('error', (err) => {
      console.error('[PythonBridge] Failed to start Python process:', err);
    });
  }

  handleMessage(message) {
    const { type, data, req_id } = message;

    if (type === 'ready') {
      this.isReady = true;
      console.log('[PythonBridge] Scraper engine initialized and ready.');
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        this.mainWindow.webContents.send('python-event', { event: 'engine_ready', data });
      }
      return;
    }

    // Check if this fulfills a pending request
    if (req_id && this.pendingRequests.has(req_id)) {
      const { resolve } = this.pendingRequests.get(req_id);
      this.pendingRequests.delete(req_id);
      resolve(data);
      return;
    }

    // Otherwise, it's a live streaming event from the scraper
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      if (type === 'scraper_event') {
        this.mainWindow.webContents.send('python-event', data);
      } else {
        this.mainWindow.webContents.send('python-event', { event: type, data });
      }
    }
  }

  sendCommand(action, payload = {}) {
    return new Promise((resolve, reject) => {
      if (!this.process || !this.process.stdin.writable) {
        return reject(new Error('Python bridge process is not running.'));
      }

      const req_id = `req_${this.requestIdCounter++}_${Date.now()}`;
      const requestPayload = {
        action,
        id: req_id,
        ...payload
      };

      this.pendingRequests.set(req_id, { resolve, reject });

      // Set timeout in case python doesn't respond
      setTimeout(() => {
        if (this.pendingRequests.has(req_id)) {
          this.pendingRequests.delete(req_id);
          reject(new Error(`Timeout waiting for response to action: ${action}`));
        }
      }, 30000);

      this.process.stdin.write(JSON.stringify(requestPayload) + '\n');
    });
  }

  stop() {
    if (this.process) {
      try {
        this.process.kill();
      } catch (err) {
        console.error('[PythonBridge] Error terminating python process:', err);
      }
      this.process = null;
    }
  }
}

module.exports = PythonBridge;
