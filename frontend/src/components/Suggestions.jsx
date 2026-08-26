import React from 'react';
import { Tag, MapPin, Stethoscope, Utensils, Fuel, Building2 } from 'lucide-react';

export default function Suggestions({
  suggestions,
  selectedCategory,
  onSelectCategory,
  selectedArea,
  onSelectArea,
  entityType,
  isScraping
}) {
  if (!suggestions) return null;

  const { categories = [], areas = [] } = suggestions;

  if (categories.length === 0 && areas.length === 0) {
    return null;
  }

  const getEntityIcon = () => {
    if (entityType === 'hospital') return <Stethoscope size={15} />;
    if (entityType === 'gas_station') return <Fuel size={15} />;
    if (entityType === 'restaurant') return <Utensils size={15} />;
    return <Building2 size={15} />;
  };

  return (
    <div className="suggestions-container" style={{ marginBottom: '16px' }}>
      {/* Category / Speciality Suggestions */}
      {categories.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div className="suggestion-group-title" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
            {getEntityIcon()}
            <span>Category Suggestions</span>
          </div>
          <div className="chips-row" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {categories.map((cat) => {
              const isSelected = selectedCategory === cat.value || (!selectedCategory && cat.id === 'all');
              return (
                <button
                  type="button"
                  key={cat.id}
                  className={`suggestion-chip ${isSelected ? 'active' : ''}`}
                  onClick={() => !isScraping && onSelectCategory(cat.value || '')}
                  disabled={isScraping}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '13px',
                    border: isSelected ? '1px solid var(--primary-color)' : '1px solid var(--border-color)',
                    background: isSelected ? 'var(--primary-color)' : 'var(--bg-card)',
                    color: isSelected ? '#fff' : 'var(--text-color)',
                    cursor: isScraping ? 'not-allowed' : 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span>{cat.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Area Suggestions */}
      {areas.length > 0 && (
        <div>
          <div className="suggestion-group-title" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
            <MapPin size={15} />
            <span>Areas</span>
          </div>
          <div className="chips-row" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            <button
              type="button"
              className={`suggestion-chip ${!selectedArea ? 'active' : ''}`}
              onClick={() => !isScraping && onSelectArea('')}
              disabled={isScraping}
              style={{
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '13px',
                border: !selectedArea ? '1px solid var(--primary-color)' : '1px solid var(--border-color)',
                background: !selectedArea ? 'var(--primary-color)' : 'var(--bg-card)',
                color: !selectedArea ? '#fff' : 'var(--text-color)',
                cursor: isScraping ? 'not-allowed' : 'pointer'
              }}
            >
              <span>All Areas</span>
            </button>
            {areas.map((area) => {
              const isSelected = selectedArea === area;
              return (
                <button
                  type="button"
                  key={area}
                  className={`suggestion-chip ${isSelected ? 'active' : ''}`}
                  onClick={() => !isScraping && onSelectArea(area)}
                  disabled={isScraping}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '13px',
                    border: isSelected ? '1px solid var(--primary-color)' : '1px solid var(--border-color)',
                    background: isSelected ? 'var(--primary-color)' : 'var(--bg-card)',
                    color: isSelected ? '#fff' : 'var(--text-color)',
                    cursor: isScraping ? 'not-allowed' : 'pointer'
                  }}
                >
                  <span>{area}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
