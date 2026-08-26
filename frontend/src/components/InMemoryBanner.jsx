import React from 'react';
import { AlertTriangle, Download } from 'lucide-react';

export default function InMemoryBanner({ inMemoryCount, onExportCsv }) {
  if (inMemoryCount === 0) return null;

  return (
    <div className="memory-banner">
      <div className="memory-banner-content">
        <AlertTriangle size={18} />
        <span>
          <strong>{inMemoryCount} records currently held in memory.</strong> They are not stored in any database. Download CSV before closing the application to prevent data loss.
        </span>
      </div>
      <button
        className="btn btn-primary"
        style={{ padding: '6px 14px', fontSize: '12.5px' }}
        onClick={onExportCsv}
      >
        <Download size={14} />
        Download CSV Now
      </button>
    </div>
  );
}
