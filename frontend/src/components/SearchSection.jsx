import React, { useRef } from 'react';
import { Search, X, Play, Square, Globe, MapPin, Tag, Loader2 } from 'lucide-react';

const EXAMPLE_QUERIES = [
  'school in Ahmedabad',
  'schools in Ahmedabad',
  'dental clinic in Satellite Road Ahmedabad',
  'hospitals in Rajkot',
  'school in Junagadh',
  'gas stations in UK',
  'hotel in London',
  'restaurant in Rajkot',
  'coaching institute in Rajkot',
  'solar panel dealer in Rajkot',
  'schools near 380015'
];

export default function SearchSection({
  searchQuery,
  setSearchQuery,
  onQueryChange,
  parsedInfo,
  onStartScraping,
  onStopScraping,
  isScraping,
  isResolving = false,
  selectedPincodesCount
}) {
  const inputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isScraping && searchQuery.trim()) {
      onStartScraping();
    }
  };

  const handleInputChange = (e) => {
    const val = e.target.value;
    if (onQueryChange) {
      onQueryChange(val);
    } else {
      setSearchQuery(val);
    }
  };

  const handleSelectExample = (query) => {
    if (isScraping) return;
    if (onQueryChange) {
      onQueryChange(query, true);
    } else {
      setSearchQuery(query);
    }
    inputRef.current?.focus();
  };

  const handleClear = () => {
    if (onQueryChange) {
      onQueryChange('');
    } else {
      setSearchQuery('');
    }
    inputRef.current?.focus();
  };

  return (
    <div className="search-card app-card">
      {/* 1. Main Search Bar + Start/Stop Button */}
      <div className="search-input-wrapper">
        <div className="search-box">
          <Search className="search-icon-left" size={20} />
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            placeholder="Search anything (e.g. school in Ahmedabad, dental clinic in Satellite Road, gas stations in UK)..."
            value={searchQuery}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={isScraping}
          />
          {searchQuery && !isScraping && (
            <button
              type="button"
              className="clear-btn"
              onClick={handleClear}
              title="Clear search"
            >
              <X size={18} />
            </button>
          )}
        </div>

        <div className="search-actions">
          {isScraping ? (
            <button
              type="button"
              className="btn btn-danger btn-scrape-action"
              onClick={onStopScraping}
            >
              <Square size={18} />
              <span>Stop Scraping</span>
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-primary btn-scrape-action"
              onClick={onStartScraping}
              disabled={!searchQuery.trim()}
            >
              {isResolving ? (
                <>
                  <Loader2 size={18} className="spin-animation" />
                  <span>Resolving query...</span>
                </>
              ) : (
                <>
                  <Play size={18} fill="currentColor" />
                  <span>Start Scraping {selectedPincodesCount > 0 ? `(${selectedPincodesCount})` : ''}</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* 2. Detected Query Badges */}
      {parsedInfo && searchQuery.trim().length >= 3 && (
        <div className="detected-badges-row">
          <span className="detected-label">Detected:</span>
          {(parsedInfo.entity_label || parsedInfo.entity_type) && (
            <span className="badge-detected badge-entity">
              <Tag size={13} />
              <span>{parsedInfo.entity_label || parsedInfo.entity_type.toUpperCase()}</span>
            </span>
          )}
          {parsedInfo.country && (
            <span className="badge-detected badge-country">
              <Globe size={13} />
              <span>{parsedInfo.country.toUpperCase()}</span>
            </span>
          )}
          {parsedInfo.city && (
            <span className="badge-detected badge-city">
              <MapPin size={13} />
              <span>{parsedInfo.city.toUpperCase()}</span>
            </span>
          )}
          {parsedInfo.area && (
            <span className="badge-detected badge-area">
              <span>Area: {parsedInfo.area}</span>
            </span>
          )}
          {parsedInfo.pincode && (
            <span className="badge-detected badge-pin">
              <span>{parsedInfo.postal_label || 'Pincode'}: {parsedInfo.pincode}</span>
            </span>
          )}
        </div>
      )}

      {/* 3. Quick Search Example Chips */}
      <div className="example-chips-container">
        <span className="example-chips-label">Examples:</span>
        <div className="example-chips-grid">
          {EXAMPLE_QUERIES.map((query, index) => (
            <button
              key={index}
              type="button"
              className="chip-tag"
              onClick={() => handleSelectExample(query)}
              disabled={isScraping}
            >
              {query}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
