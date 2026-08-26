import React from 'react';
import { DatabaseZap, Moon, Sun, Cpu, ShieldCheck, FolderArchive, Copy, LogOut, UserCheck } from 'lucide-react';

export default function Header({
  theme,
  toggleTheme,
  inMemoryCount = 0,
  duplicateCount = 0,
  historyCount = 0,
  isConnected,
  onSelectTab,
  currentUser,
  onLogout
}) {
  return (
    <header className="app-header">
      <div className="logo-section">
        <div className="logo-icon">
          <DatabaseZap size={22} />
        </div>
        <div>
          <h1 className="logo-title">DataScraper Desktop</h1>
          <p className="logo-subtitle">Intelligent Local Business Intelligence &bull; Selenium + BS4</p>
        </div>
      </div>

      <div className="header-controls">
        <div className={`status-pill ${isConnected ? 'status-pill-online' : 'status-pill-offline'}`}>
          <span className="status-dot" />
          <Cpu size={14} />
          <span>{isConnected ? 'Engine Active' : 'Connecting Engine...'}</span>
        </div>

        <button
          type="button"
          className="status-pill status-pill-memory"
          onClick={() => onSelectTab && onSelectTab('records')}
          title="Click to view Active Dataset"
        >
          <ShieldCheck size={14} />
          <span><strong>{inMemoryCount}</strong> Active</span>
        </button>

        {duplicateCount > 0 && (
          <button
            type="button"
            className="status-pill status-pill-duplicate"
            onClick={() => onSelectTab && onSelectTab('duplicates')}
            title="Click to inspect Skipped Duplicates"
          >
            <Copy size={14} />
            <span><strong>{duplicateCount}</strong> Duplicates</span>
          </button>
        )}

        <button
          type="button"
          className="status-pill status-pill-history"
          onClick={() => onSelectTab && onSelectTab('history')}
          title="Click to view Saved CSV History Files"
        >
          <FolderArchive size={14} />
          <span><strong>{historyCount}</strong> CSV Files</span>
        </button>

        <button
          className="btn-theme-toggle"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          type="button"
        >
          {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
        </button>

        {/* User Badge & Logout Option */}
        <div className="header-user-section">
          <div className="header-user-badge" title="Authenticated as Administrator">
            <UserCheck size={14} className="user-badge-icon" />
            <span className="user-badge-name">{currentUser?.username || 'Admin'}</span>
          </div>
          {onLogout && (
            <button
              type="button"
              className="btn-logout"
              onClick={onLogout}
              title="Sign Out of DataScraper"
            >
              <LogOut size={15} />
              <span>Logout</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
