import React, { useState } from 'react';
import {
  X,
  Eye,
  MapPin,
  Phone,
  Globe,
  Star,
  Clock,
  ExternalLink,
  Edit,
  Copy,
  Check,
  Building,
  Tag,
  Calendar,
  Layers,
  Info
} from 'lucide-react';

export default function ViewRecordModal({ record, isOpen, onClose, onEdit }) {
  if (!isOpen || !record) return null;

  const [copiedKey, setCopiedKey] = useState(null);

  const handleCopy = (text, key) => {
    if (!text) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(String(text));
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = String(text);
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2500);
    } catch (err) {
      console.error('Clipboard copy failed:', err);
    }
  };

  // Known / standard keys to categorize
  const knownKeys = new Set([
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

  // Extract extra / dynamic entity-specific fields (e.g. affiliation_board, admission_process, etc.)
  const extraFields = Object.entries(record).filter(([key, val]) => {
    if (knownKeys.has(key)) return false;
    if (val === null || val === undefined || val === '') return false;
    return true;
  });

  const businessName = record.name || record['Business Name'] || record['Hospital Name'] || record['School Name'] || 'Business Record';
  const category = record.category || record.Category || record['Hospital Type'] || record['School Type'] || record.entity_label || 'Listing';
  const address = record.address || record['Full Address'] || '—';
  const city = record.city || record.City || '';
  const area = record.area || record.Area || '';
  const pincode = record.pincode || record.Pincode || record['Pincode/Postcode'] || record.search_pincode || '';
  const phone = record.phone || record['Phone Number'] || '';
  const website = record.website || record.Website || '';
  const mapsUrl = record.source_url || record['Google Maps URL'] || '';
  const rating = record.rating || record['Google Rating'] || null;
  const reviewCount = record.review_count || record['Total Reviews'] || null;
  const fullTiming = record.full_timing || record['Full Timing'] || record.Timing || '';
  const openingTime = record.opening_time || record['Opening Time'] || '';
  const closingTime = record.closing_time || record['Closing Time'] || '';
  const doctorName = record.doctor_name || record['Doctor Name'] || '';
  const doctorSpeciality = record.doctor_speciality || record['Doctor Speciality'] || record.speciality || record.Speciality || '';
  const scrapedAt = record.scraped_at || record['Scraped Date/Time'] || record.skipped_at || '';
  const searchQuery = record.search_query || record['Search Query'] || '';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content view-record-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header view-record-header">
          <div className="view-header-title-wrap">
            <div className="view-header-icon-wrap">
              <Building size={20} />
            </div>
            <div>
              <div className="view-header-badge-row">
                <span className="badge-detected badge-entity">
                  <Tag size={12} />
                  <span>{category}</span>
                </span>
                {pincode && (
                  <span className="badge-detected badge-pin">
                    <MapPin size={12} />
                    <span>{pincode} {city ? `(${city})` : ''}</span>
                  </span>
                )}
                {record.status && (
                  <span className="badge-view-status">
                    {record.status}
                  </span>
                )}
              </div>
              <h2 className="view-record-title">{businessName}</h2>
            </div>
          </div>

          <button
            type="button"
            className="clear-btn btn-modal-close"
            onClick={onClose}
            title="Close dialog (Esc)"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body / Organized Info Grid */}
        <div className="view-record-body">
          {/* Quick Metrics Bar */}
          <div className="view-metrics-bar">
            <div className="view-metric-item">
              <span className="view-metric-label">Google Rating</span>
              <div className="view-metric-value-row">
                {rating ? (
                  <span className="rating-badge view-rating-badge">
                    <Star size={15} fill="#fbbf24" stroke="#f59e0b" />
                    <strong>{rating}</strong>
                    {reviewCount ? <span className="view-review-count">({reviewCount} reviews)</span> : null}
                  </span>
                ) : (
                  <span className="view-metric-empty">No rating</span>
                )}
              </div>
            </div>

            <div className="view-metric-item">
              <span className="view-metric-label">Contact Number</span>
              <div className="view-metric-value-row">
                {phone ? (
                  <a href={`tel:${phone}`} className="view-contact-link" title="Click to call">
                    <Phone size={13} />
                    <span>{phone}</span>
                  </a>
                ) : (
                  <span className="view-metric-empty">Not available</span>
                )}
                {phone && (
                  <button
                    type="button"
                    className="btn-copy-tiny"
                    onClick={() => handleCopy(phone, 'phone')}
                    title="Copy phone number"
                  >
                    {copiedKey === 'phone' ? <Check size={12} /> : <Copy size={12} />}
                  </button>
                )}
              </div>
            </div>

            <div className="view-metric-item">
              <span className="view-metric-label">Web & Navigation</span>
              <div className="view-metric-value-row" style={{ gap: '6px' }}>
                {website ? (
                  <a
                    href={website}
                    target="_blank"
                    rel="noreferrer"
                    className="table-link table-link-website"
                    title={website}
                  >
                    <Globe size={12} />
                    <span>Website</span>
                    <ExternalLink size={11} />
                  </a>
                ) : null}
                {mapsUrl ? (
                  <a
                    href={mapsUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="table-link table-link-maps"
                    title="Open on Google Maps"
                  >
                    <MapPin size={12} />
                    <span>Google Maps</span>
                    <ExternalLink size={11} />
                  </a>
                ) : null}
                {!website && !mapsUrl && <span className="view-metric-empty">None</span>}
              </div>
            </div>
          </div>

          {/* Section 1: Location & Address */}
          <div className="view-section-card">
            <div className="view-section-header">
              <MapPin size={15} />
              <h4>Location & Postal Information</h4>
            </div>
            <div className="view-section-grid">
              <div className="view-field-full">
                <span className="view-field-label">Full Address</span>
                <div className="view-address-row">
                  <p className="view-field-value view-address-text">{address}</p>
                  {address !== '—' && (
                    <button
                      type="button"
                      className="btn-copy-tiny"
                      onClick={() => handleCopy(address, 'address')}
                      title="Copy full address"
                    >
                      {copiedKey === 'address' ? <Check size={12} /> : <Copy size={12} />}
                    </button>
                  )}
                </div>
              </div>

              <div className="view-field-item">
                <span className="view-field-label">City</span>
                <span className="view-field-value">{city || '—'}</span>
              </div>

              <div className="view-field-item">
                <span className="view-field-label">Area / Locality</span>
                <span className="view-field-value">{area || '—'}</span>
              </div>

              <div className="view-field-item">
                <span className="view-field-label">Postal / Pincode</span>
                <span className="view-field-value">{pincode || '—'}</span>
              </div>

              {record.country && (
                <div className="view-field-item">
                  <span className="view-field-label">Country</span>
                  <span className="view-field-value">{record.country || 'India'}</span>
                </div>
              )}
            </div>
          </div>

          {/* Section 2: Medical / Doctor Specifics (If Available) */}
          {(doctorName || doctorSpeciality) && (
            <div className="view-section-card">
              <div className="view-section-header">
                <Info size={15} />
                <h4>Medical & Doctor Details</h4>
              </div>
              <div className="view-section-grid">
                {doctorName && (
                  <div className="view-field-item">
                    <span className="view-field-label">Doctor Name</span>
                    <span className="view-field-value" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      {doctorName}
                    </span>
                  </div>
                )}
                {doctorSpeciality && (
                  <div className="view-field-item">
                    <span className="view-field-label">Doctor Speciality</span>
                    <span className="view-field-value">{doctorSpeciality}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Section 3: Operating Hours & Schedule */}
          {(fullTiming || openingTime || closingTime) && (
            <div className="view-section-card">
              <div className="view-section-header">
                <Clock size={15} />
                <h4>Operating Hours & Timings</h4>
              </div>
              <div className="view-section-grid">
                {openingTime && (
                  <div className="view-field-item">
                    <span className="view-field-label">Opening Time</span>
                    <span className="view-field-value">{openingTime}</span>
                  </div>
                )}
                {closingTime && (
                  <div className="view-field-item">
                    <span className="view-field-label">Closing Time</span>
                    <span className="view-field-value">{closingTime}</span>
                  </div>
                )}
                {fullTiming && (
                  <div className="view-field-full">
                    <span className="view-field-label">Timing Details</span>
                    <div className="view-timing-box">
                      {fullTiming}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Section 4: All Scraped Dynamic & Custom Fields */}
          {extraFields.length > 0 && (
            <div className="view-section-card">
              <div className="view-section-header">
                <Layers size={15} />
                <h4>Extracted Attributes ({extraFields.length} fields)</h4>
              </div>
              <div className="view-section-grid">
                {extraFields.map(([key, val]) => {
                  const formattedLabel = key
                    .replace(/_/g, ' ')
                    .replace(/\b\w/g, (c) => c.toUpperCase());

                  return (
                    <div key={key} className="view-field-item">
                      <span className="view-field-label">{formattedLabel}</span>
                      <span className="view-field-value" title={String(val)}>
                        {String(val)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Section 5: Metadata & Audit Info */}
          <div className="view-section-card view-metadata-card">
            <div className="view-section-header">
              <Calendar size={14} />
              <h4>Scraper Audit Metadata</h4>
            </div>
            <div className="view-section-grid">
              <div className="view-field-item">
                <span className="view-field-label">Scraped Date / Time</span>
                <span className="view-field-value view-field-muted">{scrapedAt || '—'}</span>
              </div>
              <div className="view-field-item">
                <span className="view-field-label">Search Query</span>
                <span className="view-field-value view-field-muted">{searchQuery || '—'}</span>
              </div>
              {record.reason && (
                <div className="view-field-full">
                  <span className="view-field-label">Deduplication Note</span>
                  <span className="badge-dup-reason">{record.reason}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Actions Footer */}
        <div className="view-modal-footer">
          <button
            type="button"
            className={`btn-copy-json ${copiedKey === 'json_all' ? 'btn-copy-json-copied' : ''}`}
            onClick={() => handleCopy(JSON.stringify(record, null, 2), 'json_all')}
            title="Copy complete record details as formatted JSON"
          >
            {copiedKey === 'json_all' ? <Check size={15} strokeWidth={2.5} /> : <Copy size={15} />}
            <span>{copiedKey === 'json_all' ? 'Copied to Clipboard!' : 'Copy JSON'}</span>
          </button>

          <div className="view-modal-footer-right">
            <button
              type="button"
              className="btn btn-modal-cancel"
              onClick={onClose}
              title="Close modal (Esc)"
            >
              <X size={15} />
              <span>Close</span>
            </button>
            {onEdit && (
              <button
                type="button"
                className="btn btn-primary btn-modal-edit"
                onClick={() => onEdit(record)}
                title="Edit this record"
              >
                <Edit size={15} />
                <span>Edit Record</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
