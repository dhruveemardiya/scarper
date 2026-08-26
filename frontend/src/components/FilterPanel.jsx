import React from 'react';
import { Play, SlidersHorizontal, PlusCircle, UserPlus, Hash } from 'lucide-react';

export default function FilterPanel({
  filters,
  setFilters,
  onStartScraping,
  isScraping,
  onOpenCustomSearch,
  onOpenAddRecord,
  pincodeOptions
}) {
  const handleChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="filter-panel">
      <div className="filter-item">
        <label className="filter-label">Entity Type</label>
        <select
          className="filter-select"
          value={filters.entity_type || 'restaurant'}
          onChange={(e) => handleChange('entity_type', e.target.value)}
        >
          <option value="restaurant">Restaurant / Cafe / Food</option>
          <option value="hospital">Hospital / Clinic / Doctor</option>
          <option value="hotel">Hotel / Resort</option>
          <option value="school">School / College</option>
          <option value="gym">Gym / Fitness</option>
          <option value="salon">Salon / Spa</option>
          <option value="pharmacy">Pharmacy / Chemist</option>
        </select>
      </div>

      <div className="filter-item">
        <label className="filter-label">City</label>
        <input
          type="text"
          className="filter-input"
          placeholder="e.g. Ahmedabad"
          value={filters.city || ''}
          onChange={(e) => handleChange('city', e.target.value)}
        />
      </div>

      <div className="filter-item">
        <label className="filter-label">Area</label>
        <input
          type="text"
          className="filter-input"
          placeholder="e.g. Satellite"
          value={filters.area || ''}
          onChange={(e) => handleChange('area', e.target.value)}
        />
      </div>

      <div className="filter-item">
        <label className="filter-label">Pincode</label>
        {pincodeOptions && pincodeOptions.length > 0 ? (
          <select
            className="filter-select"
            value={filters.pincode || ''}
            onChange={(e) => handleChange('pincode', e.target.value)}
          >
            <option value="">Select / Any Pincode</option>
            {pincodeOptions.map((pin) => (
              <option key={pin} value={pin}>{pin}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            className="filter-input"
            placeholder="e.g. 380015"
            value={filters.pincode || ''}
            onChange={(e) => handleChange('pincode', e.target.value)}
          />
        )}
      </div>

      {filters.entity_type === 'restaurant' && (
        <div className="filter-item">
          <label className="filter-label">Food Preference</label>
          <select
            className="filter-select"
            value={filters.food_type || 'all'}
            onChange={(e) => handleChange('food_type', e.target.value)}
          >
            <option value="all">All (Veg & Non-Veg)</option>
            <option value="pure_veg">Pure Veg</option>
            <option value="veg">Vegetarian</option>
            <option value="non_veg">Non-Vegetarian</option>
          </select>
        </div>
      )}

      <div className="filter-item">
        <label className="filter-label">Category / Speciality</label>
        <input
          type="text"
          className="filter-input"
          placeholder="e.g. Multi-Speciality / Fine Dining"
          value={filters.category || filters.speciality || ''}
          onChange={(e) => {
            handleChange('category', e.target.value);
            handleChange('speciality', e.target.value);
          }}
        />
      </div>

      <div className="filter-item">
        <label className="filter-label">Max Records</label>
        <select
          className="filter-select"
          value={filters.max_results || 30}
          onChange={(e) => handleChange('max_results', parseInt(e.target.value, 10))}
        >
          <option value={10}>10 records</option>
          <option value={20}>20 records</option>
          <option value={30}>30 records</option>
          <option value={50}>50 records</option>
          <option value={100}>100 records</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          className="btn btn-success"
          onClick={onStartScraping}
          disabled={isScraping || (!filters.city && !filters.area && !filters.pincode && !filters.keyword)}
          style={{ minWidth: '150px' }}
        >
          <Play size={16} />
          <span>{isScraping ? 'Scraping Active...' : 'Start Scraping'}</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenCustomSearch}
          title="Manual Custom Search Parameters"
        >
          <SlidersHorizontal size={16} />
          <span>+ Custom Search</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenAddRecord}
          title="Manually Add a Business Record"
        >
          <UserPlus size={16} />
          <span>+ Add Record</span>
        </button>
      </div>
    </div>
  );
}
