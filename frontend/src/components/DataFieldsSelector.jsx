import React, { useState } from 'react';
import { Database, Plus, Check, X, Play, Square, Loader2 } from 'lucide-react';

export default function DataFieldsSelector({
  entityType,
  entityLabel,
  availableFields = [],
  selectedFields = [],
  onToggleField,
  onSelectAllFields,
  onClearAllFields,
  onAddCustomField,
  customFields = [],
  isScraping,
  onStartScraping,
  onStopScraping,
  isResolving = false,
  selectedPincodesCount = 0
}) {
  const [customInput, setCustomInput] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAdd = (e) => {
    e.preventDefault();
    const clean = customInput.trim();
    if (clean) {
      onAddCustomField(clean);
      setCustomInput('');
      setIsAdding(false);
    }
  };

  const allFields = [...availableFields, ...customFields];

  return (
    <div className="data-fields-card app-card">
      {/* Title & Bulk Action Buttons */}
      <div className="data-fields-header">
        <div className="data-fields-title-group">
          <div className="data-fields-icon-wrap">
            <Database size={18} />
          </div>
          <h3 className="data-fields-title">
            Data Fields ({entityLabel || 'Business'})
          </h3>
          <span className="data-fields-count-badge">
            {selectedFields.length} active
          </span>
        </div>

        <div className="data-fields-actions-group">
          <button
            type="button"
            className="btn btn-outline-accent btn-sm"
            onClick={onSelectAllFields}
            disabled={isScraping || allFields.length === 0}
          >
            <Check size={14} strokeWidth={2.5} />
            <span>Select All</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-neutral btn-sm"
            onClick={onClearAllFields}
            disabled={isScraping || selectedFields.length === 0}
          >
            <X size={14} strokeWidth={2} />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      {/* Field Checkbox Chips Grid */}
      <div className="data-fields-grid">
        {allFields.map((field) => {
          const isChecked = selectedFields.includes(field);
          const isCustom = customFields.includes(field);

          return (
            <label
              key={field}
              className={`field-chip ${isChecked ? (isCustom ? 'field-chip-custom-selected' : 'field-chip-selected') : 'field-chip-unselected'}`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => onToggleField(field)}
                disabled={isScraping}
                className="field-checkbox-native"
              />
              <div className="field-checkbox-custom">
                {isChecked && <Check size={11} strokeWidth={3} />}
              </div>
              <span className="field-chip-label">
                {field} {isCustom && <span className="field-custom-tag">(custom)</span>}
              </span>
            </label>
          );
        })}
      </div>

      {/* Bottom Actions Row: Add Custom Field on Left, Start Scraping Button on Right */}
      <div className="data-fields-bottom-bar">
        <div className="add-field-section">
          {!isAdding ? (
            <button
              type="button"
              className="btn btn-outline-neutral btn-sm btn-add-field-toggle"
              onClick={() => setIsAdding(true)}
              disabled={isScraping}
            >
              <Plus size={14} strokeWidth={2.5} />
              <span>Add Custom Field</span>
            </button>
          ) : (
            <form onSubmit={handleAdd} className="add-field-form">
              <input
                type="text"
                placeholder="e.g. Email Address / Special Discount"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                className="add-field-input"
                autoFocus
                disabled={isScraping}
              />
              <button
                type="submit"
                className="btn btn-primary btn-sm"
                disabled={isScraping || !customInput.trim()}
              >
                Add Field
              </button>
              <button
                type="button"
                className="btn btn-outline-neutral btn-sm"
                onClick={() => {
                  setIsAdding(false);
                  setCustomInput('');
                }}
              >
                Cancel
              </button>
            </form>
          )}
        </div>

        {/* Primary Start Scraping Button at Bottom Right */}
        {onStartScraping && (
          <div className="data-fields-start-action">
            {isScraping ? (
              <button
                type="button"
                className="btn btn-danger btn-scrape-action"
                onClick={onStopScraping}
                title="Stop current scraping process"
              >
                <Square size={16} fill="currentColor" />
                <span>Stop Scraping</span>
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary btn-scrape-action"
                onClick={onStartScraping}
                disabled={isResolving || selectedPincodesCount === 0 || selectedFields.length === 0}
                title="Start extracting data for selected postal codes and data fields"
              >
                {isResolving ? (
                  <>
                    <Loader2 size={16} className="spin-animation" />
                    <span>Resolving...</span>
                  </>
                ) : (
                  <>
                    <Play size={16} fill="currentColor" />
                    <span>
                      {selectedPincodesCount > 0
                        ? `Start Scraping (${selectedPincodesCount})`
                        : 'Start Scraping'}
                    </span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
