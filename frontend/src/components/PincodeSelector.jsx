import React, { useState } from 'react';
import { MapPin, Check, X, Plus, Loader2, Info } from 'lucide-react';

export default function PincodeSelector({
  city,
  postalLabel = 'Pincode',
  pincodes = [],
  selectedPincodes = [],
  onTogglePincode,
  onSelectAll,
  onClearAll,
  onAddCustomPincode,
  isScraping,
  isResolving = false
}) {
  const [customInput, setCustomInput] = useState('');

  const handleAddCustom = (e) => {
    e.preventDefault();
    const clean = customInput.trim().toUpperCase();
    if (clean) {
      onAddCustomPincode(clean);
      setCustomInput('');
    }
  };

  return (
    <div className="pincode-section-card app-card">
      {/* 1. Header Bar: Title + Selected Count + Select/Clear Controls */}
      <div className="pincode-header-row">
        <div className="pincode-title-group">
          <div className="pincode-icon-wrap">
            <MapPin size={18} />
          </div>
          <h3 className="pincode-section-title">
            {city ? `${city} ${postalLabel}s` : `Select ${postalLabel}s`}
          </h3>
          <span className="pincode-count-badge">
            {selectedPincodes.length} selected
          </span>
        </div>

        <div className="pincode-actions-group">
          <button
            type="button"
            className="btn btn-outline-accent btn-sm"
            onClick={onSelectAll}
            disabled={isScraping || isResolving || pincodes.length === 0}
          >
            <Check size={14} strokeWidth={2.5} />
            <span>Select All</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-neutral btn-sm"
            onClick={onClearAll}
            disabled={isScraping || isResolving || selectedPincodes.length === 0}
          >
            <X size={14} strokeWidth={2} />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      {/* 2. Loading State vs Pincode Chips Grid */}
      {isResolving ? (
        <div className="pincode-resolving-state" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', padding: '28px 0', color: 'var(--text-muted)' }}>
          <Loader2 size={18} className="spin-animation" style={{ color: 'var(--accent)' }} />
          <span style={{ fontSize: '13.5px', fontWeight: 500 }}>
            Resolving {city ? `${city} location` : 'location'} and finding postal codes...
          </span>
        </div>
      ) : pincodes.length === 0 ? (
        <div className="pincode-empty-state" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '20px', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', color: 'var(--text-muted)', fontSize: '13px' }}>
          <Info size={16} style={{ color: 'var(--accent)', flexShrink: 0 }} />
          <span>
            No verified automatic {postalLabel.toLowerCase()}s found for {city || 'this location'}. You can manually enter one below.
          </span>
        </div>
      ) : (
        <div className="pincode-chips-grid">
          {pincodes.map((pin) => {
            const isChecked = selectedPincodes.includes(pin);
            return (
              <button
                key={pin}
                type="button"
                className={`pincode-chip ${isChecked ? 'pincode-chip-selected' : 'pincode-chip-unselected'}`}
                onClick={() => !isScraping && onTogglePincode(pin)}
                disabled={isScraping}
              >
                <div className="pincode-checkbox-box">
                  {isChecked && <Check size={12} strokeWidth={3} />}
                </div>
                <span className="pincode-chip-text">{pin}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* 3. Manual Add Pincode Bar */}
      <form onSubmit={handleAddCustom} className="pincode-add-form">
        <div className="pincode-add-input-wrap">
          <input
            type="text"
            className="pincode-add-input"
            placeholder={`Enter ${postalLabel} (e.g. 360001 / LE18)`}
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            disabled={isScraping || isResolving}
          />
        </div>
        <button
          type="submit"
          className="btn btn-primary btn-add-pincode"
          disabled={isScraping || isResolving || !customInput.trim()}
        >
          <Plus size={16} strokeWidth={2.5} />
          <span>Add</span>
        </button>
      </form>
    </div>
  );
}
