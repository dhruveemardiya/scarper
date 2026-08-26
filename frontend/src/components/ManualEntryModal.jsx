import React, { useState } from 'react';
import { X, SlidersHorizontal, UserPlus, Play } from 'lucide-react';

export default function ManualEntryModal({
  isOpen,
  mode, // 'custom_search' | 'add_record'
  onClose,
  onStartCustomSearch,
  onAddManualRecord
}) {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState(mode || 'custom_search');

  // Custom Search Form State
  const [searchParams, setSearchParams] = useState({
    entity_type: 'restaurant',
    city: '',
    area: '',
    pincode: '',
    category: '',
    speciality: '',
    food_type: 'all',
    keyword: '',
    max_results: 30
  });

  // Manual Record Form State
  const [recordData, setRecordData] = useState({
    name: '',
    entity_type: 'restaurant',
    category: '',
    sub_category: '',
    veg_type: 'all',
    speciality: '',
    doctor_name: '',
    doctor_speciality: '',
    address: '',
    area: '',
    city: '',
    pincode: '',
    phone: '',
    rating: 4.5,
    review_count: 50,
    full_timing: '10:00 AM – 10:00 PM',
    website: '',
    source_url: ''
  });

  const handleCustomSearchSubmit = (e) => {
    e.preventDefault();
    onStartCustomSearch(searchParams);
    onClose();
  };

  const handleManualRecordSubmit = (e) => {
    e.preventDefault();
    onAddManualRecord({
      ...recordData,
      id: 'manual_' + Date.now(),
      status: 'Manual',
      scraped_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className={`btn ${activeTab === 'custom_search' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '13px' }}
              onClick={() => setActiveTab('custom_search')}
            >
              <SlidersHorizontal size={14} />
              <span>Custom Search</span>
            </button>
            <button
              type="button"
              className={`btn ${activeTab === 'add_record' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '13px' }}
              onClick={() => setActiveTab('add_record')}
            >
              <UserPlus size={14} />
              <span>Add Manual Record</span>
            </button>
          </div>

          <button className="clear-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {activeTab === 'custom_search' ? (
          <form onSubmit={handleCustomSearchSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Entity / Business Type</label>
                <select
                  className="filter-select"
                  value={searchParams.entity_type}
                  onChange={(e) => setSearchParams({ ...searchParams, entity_type: e.target.value })}
                >
                  <option value="restaurant">Restaurant</option>
                  <option value="hospital">Hospital / Doctor</option>
                  <option value="hotel">Hotel</option>
                  <option value="school">School / College</option>
                  <option value="gym">Gym / Fitness</option>
                  <option value="salon">Salon</option>
                  <option value="pharmacy">Pharmacy</option>
                </select>
              </div>

              <div className="filter-item">
                <label className="filter-label">City</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Ahmedabad"
                  value={searchParams.city}
                  onChange={(e) => setSearchParams({ ...searchParams, city: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Area (Optional)</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Satellite"
                  value={searchParams.area}
                  onChange={(e) => setSearchParams({ ...searchParams, area: e.target.value })}
                />
              </div>

              <div className="filter-item">
                <label className="filter-label">Pincode (Optional)</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. 380015"
                  value={searchParams.pincode}
                  onChange={(e) => setSearchParams({ ...searchParams, pincode: e.target.value })}
                />
              </div>
            </div>

            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Category / Speciality</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Multi-Speciality / Fine Dining"
                  value={searchParams.category}
                  onChange={(e) => setSearchParams({ ...searchParams, category: e.target.value, speciality: e.target.value })}
                />
              </div>

              {searchParams.entity_type === 'restaurant' && (
                <div className="filter-item">
                  <label className="filter-label">Food Preference</label>
                  <select
                    className="filter-select"
                    value={searchParams.food_type}
                    onChange={(e) => setSearchParams({ ...searchParams, food_type: e.target.value })}
                  >
                    <option value="all">All</option>
                    <option value="pure_veg">Pure Veg</option>
                    <option value="veg">Veg</option>
                    <option value="non_veg">Non-Veg</option>
                  </select>
                </div>
              )}
            </div>

            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Additional Search Keywords</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. 24 hours, rooftop, jain food"
                  value={searchParams.keyword}
                  onChange={(e) => setSearchParams({ ...searchParams, keyword: e.target.value })}
                />
              </div>

              <div className="filter-item">
                <label className="filter-label">Max Results</label>
                <select
                  className="filter-select"
                  value={searchParams.max_results}
                  onChange={(e) => setSearchParams({ ...searchParams, max_results: parseInt(e.target.value, 10) })}
                >
                  <option value={10}>10 records</option>
                  <option value={30}>30 records</option>
                  <option value={50}>50 records</option>
                  <option value={100}>100 records</option>
                </select>
              </div>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                <Play size={16} />
                Start Custom Scraping
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleManualRecordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Business / Hospital Name</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Apex Multi-Speciality Hospital"
                  value={recordData.name}
                  onChange={(e) => setRecordData({ ...recordData, name: e.target.value })}
                  required
                />
              </div>

              <div className="filter-item">
                <label className="filter-label">Entity Type</label>
                <select
                  className="filter-select"
                  value={recordData.entity_type}
                  onChange={(e) => setRecordData({ ...recordData, entity_type: e.target.value })}
                >
                  <option value="restaurant">Restaurant</option>
                  <option value="hospital">Hospital</option>
                  <option value="hotel">Hotel</option>
                  <option value="school">School</option>
                  <option value="gym">Gym</option>
                  <option value="salon">Salon</option>
                  <option value="pharmacy">Pharmacy</option>
                </select>
              </div>
            </div>

            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">City</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Rajkot"
                  value={recordData.city}
                  onChange={(e) => setRecordData({ ...recordData, city: e.target.value })}
                />
              </div>

              <div className="filter-item">
                <label className="filter-label">Area</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. Kalawad Road"
                  value={recordData.area}
                  onChange={(e) => setRecordData({ ...recordData, area: e.target.value })}
                />
              </div>
            </div>

            <div className="modal-grid">
              <div className="filter-item">
                <label className="filter-label">Pincode</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. 360005"
                  value={recordData.pincode}
                  onChange={(e) => setRecordData({ ...recordData, pincode: e.target.value })}
                />
              </div>

              <div className="filter-item">
                <label className="filter-label">Phone</label>
                <input
                  type="text"
                  className="filter-input"
                  placeholder="e.g. +91 98765 43210"
                  value={recordData.phone}
                  onChange={(e) => setRecordData({ ...recordData, phone: e.target.value })}
                />
              </div>
            </div>

            {recordData.entity_type === 'hospital' && (
              <div className="modal-grid">
                <div className="filter-item">
                  <label className="filter-label">Doctor Name</label>
                  <input
                    type="text"
                    className="filter-input"
                    placeholder="e.g. Dr. K. M. Shah"
                    value={recordData.doctor_name}
                    onChange={(e) => setRecordData({ ...recordData, doctor_name: e.target.value })}
                  />
                </div>

                <div className="filter-item">
                  <label className="filter-label">Speciality</label>
                  <input
                    type="text"
                    className="filter-input"
                    placeholder="e.g. Cardiology"
                    value={recordData.speciality}
                    onChange={(e) => setRecordData({ ...recordData, speciality: e.target.value, doctor_speciality: e.target.value })}
                  />
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-success">
                <UserPlus size={16} />
                Add Record to Memory
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
