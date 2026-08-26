import React from 'react';
import {
  FileSpreadsheet,
  CheckCircle2,
  AlertOctagon,
  Copy,
  Loader2,
  MapPin,
  TrendingUp,
  RefreshCw,
  Check
} from 'lucide-react';

export default function ProgressHUD({
  stats,
  isScraping,
  statusMessage,
  onStopScraping,
  pincodeQueue = [],
  pincodeStatuses = {},
  currentListingInfo,
  outputCsvPath,
  onSelectTab
}) {
  const {
    found = 0,
    collected = 0,
    duplicates = 0,
    failed = 0,
    progress_pct = 0,
    current_pincode = '',
    pincode_index = 0,
    pincode_total = 0
  } = stats || {};

  return (
    <div className="progress-hud-card app-card">
      {/* Top Status Header */}
      <div className="hud-header">
        <div className="hud-status-badge">
          {isScraping ? (
            <>
              <div className="pulse-dot" />
              <Loader2 className="spin-animation" size={17} />
              <span className="hud-status-text hud-status-active">
                {statusMessage || `Scraping ${current_pincode ? `Postal Code ${current_pincode}` : 'Google Maps'}...`}
              </span>
            </>
          ) : (
            <>
              <CheckCircle2 size={18} className="hud-status-complete-icon" />
              <span className="hud-status-text hud-status-complete">
                {statusMessage || (collected > 0 ? `${collected} Records Written to CSV` : 'Ready')}
              </span>
            </>
          )}
        </div>

        {outputCsvPath && (
          <div className="hud-csv-path" title={`Target CSV File: ${outputCsvPath}`}>
            <FileSpreadsheet size={14} />
            <span className="hud-csv-text">{outputCsvPath.split(/[\\/]/).pop()}</span>
          </div>
        )}
      </div>

      {/* Metrics Row: 5 Clean Stat Cards */}
      <div className="hud-metrics-grid">
        {/* Card 1: Current Postal Code */}
        <div className="metric-card metric-card-accent">
          <div className="metric-header">
            <span className="metric-label">Current Pincode</span>
            <MapPin size={15} className="metric-icon" />
          </div>
          <div className="metric-value">
            {current_pincode || (pincodeQueue[0] || '—')}
          </div>
          <div className="metric-subtext">
            {pincode_total > 0 ? `Queue ${pincode_index} of ${pincode_total}` : 'Active Queue'}
          </div>
        </div>

        {/* Card 2: Written to CSV */}
        <div
          className="metric-card metric-card-success metric-card-clickable"
          onClick={() => onSelectTab && onSelectTab('records')}
          title="Click to view collected dataset in table"
        >
          <div className="metric-header">
            <span className="metric-label">Written to CSV</span>
            <FileSpreadsheet size={15} className="metric-icon" />
          </div>
          <div className="metric-value metric-value-success">
            {collected}
          </div>
          <div className="metric-subtext">
            Click to view dataset &rarr;
          </div>
        </div>

        {/* Card 3: Duplicates Skipped */}
        <div
          className={`metric-card metric-card-warning ${duplicates > 0 ? 'metric-card-clickable' : ''}`}
          onClick={() => onSelectTab && onSelectTab('duplicates')}
          title="Click to inspect skipped duplicate listings"
        >
          <div className="metric-header">
            <span className="metric-label">Duplicates Skipped</span>
            <Copy size={15} className="metric-icon" />
          </div>
          <div className="metric-value metric-value-warning">
            {duplicates}
          </div>
          <div className="metric-subtext">
            {duplicates > 0 ? 'Click to inspect log &rarr;' : 'Cross-pincode deduped'}
          </div>
        </div>

        {/* Card 4: Failed / Retried */}
        <div className="metric-card metric-card-danger">
          <div className="metric-header">
            <span className="metric-label">Failed / Retried</span>
            <AlertOctagon size={15} className="metric-icon" />
          </div>
          <div className="metric-value metric-value-danger">
            {failed}
          </div>
          <div className="metric-subtext">
            Auto-recovered attempts
          </div>
        </div>

        {/* Card 5: Queue Progress */}
        <div className="metric-card metric-card-progress">
          <div className="metric-header">
            <span className="metric-label">Queue Progress</span>
            <TrendingUp size={15} className="metric-icon" />
          </div>
          <div className="metric-value metric-value-accent">
            {progress_pct}%
          </div>
          <div className="progress-bar-wrap">
            <div
              className="progress-bar-fill"
              style={{ width: `${Math.min(100, Math.max(0, progress_pct))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Pincode Queue Flow Chips */}
      {pincodeQueue.length > 0 && (
        <div className="hud-queue-container">
          <div className="hud-queue-header">
            <div className="hud-queue-title">
              <MapPin size={14} />
              <span>Queue Status ({pincodeQueue.length} Postal Codes)</span>
            </div>
            {currentListingInfo && (
              <span className="hud-listing-ticker">
                Extracting Listing {currentListingInfo.index} / {currentListingInfo.total}: <strong>{currentListingInfo.label}</strong>
              </span>
            )}
          </div>

          <div className="hud-queue-chips">
            {pincodeQueue.map((pin) => {
              const status = pincodeStatuses[pin] || (pin === current_pincode ? 'scraping' : 'pending');
              const isCurrent = pin === current_pincode && isScraping;

              let statusClass = 'chip-queue-pending';
              let icon = null;

              if (status === 'completed') {
                statusClass = 'chip-queue-completed';
                icon = <Check size={12} strokeWidth={2.5} />;
              } else if (isCurrent || status === 'scraping') {
                statusClass = 'chip-queue-active';
                icon = <RefreshCw size={12} className="spin-animation" />;
              } else if (status === 'failed') {
                statusClass = 'chip-queue-failed';
                icon = <AlertOctagon size={12} />;
              }

              return (
                <span key={pin} className={`chip-queue-item ${statusClass}`}>
                  {icon}
                  <span>{pin}</span>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
