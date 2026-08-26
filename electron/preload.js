const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Python Bridge Invocation
  sendToPython: (action, payload = {}) => ipcRenderer.invoke('python-command', { action, ...payload }),
  
  // Python Scraper Event Listener
  onPythonEvent: (callback) => {
    const subscription = (event, value) => callback(value);
    ipcRenderer.on('python-event', subscription);
    return () => ipcRenderer.removeListener('python-event', subscription);
  },

  // Save CSV Native Dialog
  showSaveDialog: (defaultFilename) => ipcRenderer.invoke('show-save-dialog', defaultFilename),

  // Confirm exit with unsaved records
  onAppClosing: (callback) => {
    ipcRenderer.on('app-closing-check', callback);
  },
  respondToClosing: (shouldClose) => ipcRenderer.send('app-closing-response', shouldClose)
});
