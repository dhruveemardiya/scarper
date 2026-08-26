const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const PythonBridge = require('./python_bridge');

let mainWindow = null;
let pythonBridge = null;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#0f172a',
    title: 'Data Scraper - Local Business Intelligence',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  });

  // Start Python Bridge
  pythonBridge = new PythonBridge(mainWindow);
  pythonBridge.start();

  mainWindow.maximize();

  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.setZoomLevel(0);
  });

  const devUrl = 'http://localhost:5173';
  mainWindow.loadURL(devUrl).catch(() => {
    // If dev server not yet ready, load built dist or retry
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html')).catch((err) => {
      console.log('[Electron] Loading dev URL, waiting for Vite...', err);
    });
  });

  // Handle window close event
  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault();
      // Ask React UI if there are in-memory records
      mainWindow.webContents.send('app-closing-check');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (pythonBridge) {
      pythonBridge.stop();
    }
  });
}

// IPC Handlers
ipcMain.handle('python-command', async (event, payload) => {
  if (!pythonBridge) {
    throw new Error('Python bridge not initialized');
  }
  const { action, ...params } = payload;
  return await pythonBridge.sendCommand(action, params);
});

ipcMain.handle('show-save-dialog', async (event, defaultFilename) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Scraped Dataset as CSV',
    defaultPath: defaultFilename || 'scraped_businesses.csv',
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

ipcMain.on('app-closing-response', (event, shouldClose) => {
  if (shouldClose) {
    isQuitting = true;
    if (pythonBridge) {
      pythonBridge.stop();
    }
    if (mainWindow) {
      mainWindow.destroy();
    }
    app.quit();
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pythonBridge) {
      pythonBridge.stop();
    }
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  if (pythonBridge) {
    pythonBridge.stop();
  }
});
