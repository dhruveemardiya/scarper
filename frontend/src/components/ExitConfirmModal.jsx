import React from 'react';
import { AlertTriangle, Download, LogOut, X } from 'lucide-react';

export default function ExitConfirmModal({ isOpen, unsavedCount, onDownloadAndExit, onExitWithoutSaving, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" style={{ zIndex: 1100 }}>
      <div className="modal-content" style={{ maxWidth: '480px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#f59e0b' }}>
            <AlertTriangle size={24} />
            <h3 className="modal-title" style={{ fontSize: '18px' }}>Unsaved In-Memory Records</h3>
          </div>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.6 }}>
          You have <strong style={{ color: '#fff' }}>{unsavedCount} business records</strong> stored in memory. Since there is no database, closing now will permanently discard all unsaved data.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px' }}>
          <button className="btn btn-primary" onClick={onDownloadAndExit}>
            <Download size={16} />
            <span>Download CSV & Exit</span>
          </button>

          <button className="btn btn-danger" onClick={onExitWithoutSaving}>
            <LogOut size={16} />
            <span>Exit Without Saving</span>
          </button>

          <button className="btn btn-secondary" onClick={onCancel}>
            <X size={16} />
            <span>Cancel (Stay in App)</span>
          </button>
        </div>
      </div>
    </div>
  );
}
