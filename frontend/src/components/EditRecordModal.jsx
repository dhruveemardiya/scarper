import React, { useState, useEffect } from 'react';
import {
  X,
  Save,
  Building,
  MapPin,
  Phone,
  Globe,
  Star,
  Clock,
  Edit3,
  Layers,
  Check
} from 'lucide-react';

export default function EditRecordModal({ record, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (record) {
      setFormData({ ...record });
    }
  }, [record]);

  if (!isOpen || !record) return null;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ ...formData, status: 'Edited' });
    onClose();
  };

  const isHospital =
    formData.entity_type === 'hospital' ||
    (formData.category && String(formData.category).toLowerCase().includes('hospital')) ||
    (formData.category && String(formData.category).toLowerCase().includes('clinic')) ||
    (formData.category && String(formData.category).toLowerCase().includes('doctor'));

  const isRestaurant =
    formData.entity_type === 'restaurant' ||
    (formData.category && String(formData.category).toLowerCase().includes('restaurant')) ||
    (formData.category && String(formData.category).toLowerCase().includes('cafe')) ||
    (formData.category && String(formData.category).toLowerCase().includes('food'));

  // Standard keys to exclude from extra dynamic fields section
  const standardKeys = new Set([
    'id', 'name', 'Business Name', 'Hospital Name', 'School Name', 'Restaurant Name', 'Institute Name',
    'category', 'Category', 'Hospital Type', 'School Type', 'entity_type', 'entity_label',
    'address', 'Full Address', 'area', 'Area', 'city', 'City', 'country', 'Country',
    'pincode', 'Pincode', 'Pincode/Postcode', 'postcode', 'search_pincode', 'Search Pincode/Postcode',
    'phone', 'Phone Number', 'Phone', 'website', 'Website', 'source_url', 'Google Maps URL',
    'rating', 'Google Rating', 'review_count', 'Total Reviews', 'price_range', 'Price Range',
    'opening_time', 'Opening Time', 'closing_time', 'Closing Time', 'full_timing', 'Full Timing', 'Timing',
    'doctor_name', 'Doctor Name', 'doctor_speciality', 'Doctor Speciality', 'speciality', 'Speciality', 'sub_speciality',
    'veg_type', 'Veg / Non-Veg', 'latitude', 'Latitude', 'longitude', 'Longitude',
    'search_query', 'Search Query', 'scraped_at', 'Scraped Date/Time', 'status', 'reason', 'skipped_at',
    'duplicate_hash'
  ]);

  const customFieldEntries = Object.entries(formData).filter(
    ([k]) => !standardKeys.has(k) && typeof formData[k] !== 'object'
  );

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content edit-record-modal-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* Modal Header */}
        <div className="modal-header edit-modal-header">
          <div className="edit-header-title-wrap">
            <div className="edit-header-icon-wrap">
              <Edit3 size={20} />
            </div>
            <div>
              <h3 className="edit-modal-title">Edit Business Record</h3>
              <p className="edit-modal-subtitle">
                Editing: <strong>{formData.name || 'Untitled Record'}</strong>
              </p>
            </div>
          </div>

          <button
            type="button"
            className="btn-modal-close"
            onClick={onClose}
            title="Close dialog (Esc)"
          >
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="edit-modal-form">
          <div className="edit-modal-body">
            {/* Section 1: Core Information */}
            <div className="edit-section-card">
              <div className="edit-section-header">
                <Building size={16} />
                <h4>Primary Business Information</h4>
              </div>
              <div className="edit-grid-2">
                <div className="edit-form-group edit-span-2">
                  <label className="edit-form-label">
                    Business / Entity Name <span className="required-star">*</span>
                  </label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="Enter business name..."
                    value={formData.name || ''}
                    onChange={(e) => handleChange('name', e.target.value)}
                    required
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Category / Business Type</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. Dental Clinic, School, Restaurant"
                    value={formData.category || ''}
                    onChange={(e) => handleChange('category', e.target.value)}
                  />
                </div>

                {isHospital && (
                  <>
                    <div className="edit-form-group">
                      <label className="edit-form-label">Doctor Name</label>
                      <input
                        type="text"
                        className="edit-form-input"
                        placeholder="e.g. Dr. Rajesh Patel"
                        value={formData.doctor_name || ''}
                        onChange={(e) => handleChange('doctor_name', e.target.value)}
                      />
                    </div>
                    <div className="edit-form-group">
                      <label className="edit-form-label">Doctor Speciality</label>
                      <input
                        type="text"
                        className="edit-form-input"
                        placeholder="e.g. Cardiologist, Dentist"
                        value={formData.doctor_speciality || ''}
                        onChange={(e) => handleChange('doctor_speciality', e.target.value)}
                      />
                    </div>
                  </>
                )}

                {isRestaurant && (
                  <>
                    <div className="edit-form-group">
                      <label className="edit-form-label">Veg / Non-Veg Dining</label>
                      <select
                        className="edit-form-select"
                        value={formData.veg_type || 'all'}
                        onChange={(e) => handleChange('veg_type', e.target.value)}
                      >
                        <option value="all">Both / Multi-Cuisine</option>
                        <option value="pure_veg">Pure Veg</option>
                        <option value="veg">Veg</option>
                        <option value="non_veg">Non-Veg</option>
                      </select>
                    </div>
                    <div className="edit-form-group">
                      <label className="edit-form-label">Price Range</label>
                      <input
                        type="text"
                        className="edit-form-input"
                        placeholder="e.g. ₹₹ (Moderate)"
                        value={formData.price_range || ''}
                        onChange={(e) => handleChange('price_range', e.target.value)}
                      />
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Section 2: Contact & Location */}
            <div className="edit-section-card">
              <div className="edit-section-header">
                <MapPin size={16} />
                <h4>Location & Contact Information</h4>
              </div>
              <div className="edit-grid-2">
                <div className="edit-form-group edit-span-2">
                  <label className="edit-form-label">Full Address</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="Enter complete physical address..."
                    value={formData.address || ''}
                    onChange={(e) => handleChange('address', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Phone Number</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. +91 98765 43210"
                    value={formData.phone || ''}
                    onChange={(e) => handleChange('phone', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Pincode / Postal Code</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. 380015"
                    value={formData.pincode || ''}
                    onChange={(e) => handleChange('pincode', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Area / Locality</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. Satellite Road"
                    value={formData.area || ''}
                    onChange={(e) => handleChange('area', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">City</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. Ahmedabad"
                    value={formData.city || ''}
                    onChange={(e) => handleChange('city', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Website URL</label>
                  <input
                    type="url"
                    className="edit-form-input"
                    placeholder="https://..."
                    value={formData.website || ''}
                    onChange={(e) => handleChange('website', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Google Maps URL</label>
                  <input
                    type="url"
                    className="edit-form-input"
                    placeholder="https://maps.google.com/..."
                    value={formData.source_url || ''}
                    onChange={(e) => handleChange('source_url', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Section 3: Ratings & Timings */}
            <div className="edit-section-card">
              <div className="edit-section-header">
                <Clock size={16} />
                <h4>Ratings & Operating Timings</h4>
              </div>
              <div className="edit-grid-2">
                <div className="edit-form-group">
                  <label className="edit-form-label">Google Rating (1.0 - 5.0)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1.0"
                    max="5.0"
                    className="edit-form-input"
                    placeholder="e.g. 4.8"
                    value={formData.rating !== undefined && formData.rating !== null ? formData.rating : ''}
                    onChange={(e) => handleChange('rating', e.target.value ? parseFloat(e.target.value) : '')}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Total Reviews</label>
                  <input
                    type="number"
                    min="0"
                    className="edit-form-input"
                    placeholder="e.g. 150"
                    value={formData.review_count !== undefined && formData.review_count !== null ? formData.review_count : ''}
                    onChange={(e) => handleChange('review_count', e.target.value ? parseInt(e.target.value, 10) : '')}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Opening Time</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. 09:00 AM"
                    value={formData.opening_time || ''}
                    onChange={(e) => handleChange('opening_time', e.target.value)}
                  />
                </div>

                <div className="edit-form-group">
                  <label className="edit-form-label">Closing Time</label>
                  <input
                    type="text"
                    className="edit-form-input"
                    placeholder="e.g. 08:00 PM"
                    value={formData.closing_time || ''}
                    onChange={(e) => handleChange('closing_time', e.target.value)}
                  />
                </div>

                <div className="edit-form-group edit-span-2">
                  <label className="edit-form-label">Full Timing Schedule</label>
                  <textarea
                    rows={2}
                    className="edit-form-textarea"
                    placeholder="e.g. Mon-Sat: 9:00 AM – 8:00 PM | Sun: Closed"
                    value={formData.full_timing || ''}
                    onChange={(e) => handleChange('full_timing', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Section 4: Dynamic & Custom Fields */}
            {customFieldEntries.length > 0 && (
              <div className="edit-section-card">
                <div className="edit-section-header">
                  <Layers size={16} />
                  <h4>Additional Custom Fields</h4>
                </div>
                <div className="edit-grid-2">
                  {customFieldEntries.map(([key, val]) => {
                    const formattedLabel = key
                      .replace(/_/g, ' ')
                      .replace(/\b\w/g, (c) => c.toUpperCase());

                    return (
                      <div key={key} className="edit-form-group">
                        <label className="edit-form-label">{formattedLabel}</label>
                        <input
                          type="text"
                          className="edit-form-input"
                          value={val || ''}
                          onChange={(e) => handleChange(key, e.target.value)}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Modal Footer Actions */}
          <div className="edit-modal-footer">
            <button
              type="button"
              className="btn btn-modal-cancel"
              onClick={onClose}
              title="Cancel edits and close (Esc)"
            >
              <X size={15} />
              <span>Cancel</span>
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-save-record"
            >
              <Save size={16} />
              <span>Save Record</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
