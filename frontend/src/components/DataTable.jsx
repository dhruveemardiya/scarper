import React, { useState, useMemo } from 'react';
import {
  Download,
  Trash2,
  Edit,
  Search,
  Star,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ExternalLink,
  FileSpreadsheet,
  Copy,
  FolderArchive,
  CheckCircle2,
  AlertTriangle,
  PlusCircle,
  Clock,
  RotateCw,
  FolderOpen,
  Eye
} from 'lucide-react';

export default function DataTable({
  records = [],
  duplicates = [],
  historyFiles = [],
  entityType = 'business',
  selectedFields = [],
  onViewRecord,
  onEditRecord,
  onDeleteRecord,
  onClearAll,
  onExportCsv,
  onLoadHistoryCsv,
  onDeleteHistoryCsv,
  onForceIncludeDuplicate,
  onClearDuplicates,
  onRefreshHistory,
  defaultCsvFileName = 'export.csv',
  activeTab = 'records',
  setActiveTab
}) {
  const [currentTab, setCurrentTab] = useState('records');
  const tab = setActiveTab ? activeTab : currentTab;
  const setTab = setActiveTab || setCurrentTab;

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [dupSearchTerm, setDupSearchTerm] = useState('');
  const [histSearchTerm, setHistSearchTerm] = useState('');

  // Sorting: default to '' (natural newest-scraped-first streaming order)
  const [sortField, setSortField] = useState('');
  const [sortAsc, setSortAsc] = useState(true);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [customCsvName, setCustomCsvName] = useState('');

  const currentExportName = customCsvName.trim() || defaultCsvFileName || 'scraped_records.csv';

  const handleSort = (field) => {
    if (sortField === field) {
      if (!sortAsc) {
        // Reset to live newest-first streaming order
        setSortField('');
        setSortAsc(true);
      } else {
        setSortAsc(false);
      }
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  // Filtered & Sorted Active Records
  const filteredAndSortedRecords = useMemo(() => {
    let list = [...records];
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter((r) =>
        Object.values(r).some((v) =>
          typeof v === 'string' ? v.toLowerCase().includes(q) : false
        )
      );
    }

    if (sortField) {
      list.sort((a, b) => {
        let valA = a[sortField] || '';
        let valB = b[sortField] || '';
        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortAsc ? valA - valB : valB - valA;
        }
        return sortAsc
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      });
    }

    return list;
  }, [records, searchTerm, sortField, sortAsc]);

  // Filtered Duplicates
  const filteredDuplicates = useMemo(() => {
    let list = [...duplicates];
    if (dupSearchTerm.trim()) {
      const q = dupSearchTerm.toLowerCase();
      list = list.filter((d) =>
        Object.values(d).some((v) =>
          typeof v === 'string' ? v.toLowerCase().includes(q) : false
        )
      );
    }
    return list;
  }, [duplicates, dupSearchTerm]);

  // Filtered History Files
  const filteredHistoryFiles = useMemo(() => {
    let list = [...historyFiles];
    if (histSearchTerm.trim()) {
      const q = histSearchTerm.toLowerCase();
      list = list.filter((f) =>
        (f.filename || '').toLowerCase().includes(q) ||
        (f.filepath || '').toLowerCase().includes(q)
      );
    }
    return list;
  }, [historyFiles, histSearchTerm]);

  // Pagination for Active Records
  const totalPages = Math.ceil(filteredAndSortedRecords.length / pageSize) || 1;
  const currentRecords = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSortedRecords.slice(start, start + pageSize);
  }, [filteredAndSortedRecords, currentPage, pageSize]);

  // Pagination for Duplicates
  const [dupPage, setDupPage] = useState(1);
  const totalDupPages = Math.ceil(filteredDuplicates.length / pageSize) || 1;
  const currentDuplicates = useMemo(() => {
    const start = (dupPage - 1) * pageSize;
    return filteredDuplicates.slice(start, start + pageSize);
  }, [filteredDuplicates, dupPage, pageSize]);

  // Helper to map field name to object key
  const getFieldKey = (fieldName) => {
    const lower = fieldName.toLowerCase().trim();
    if (lower === 'name' || lower === 'business name' || lower === 'school name' || lower === 'restaurant name' || lower === 'hospital name' || lower === 'institute name') return 'name';
    if (lower.includes('doctor name') || lower.includes('key doctors')) return 'doctor_name';
    if (lower.includes('principal') || lower.includes('head name')) return 'principal_name';
    if (lower.includes('faculty') || lower.includes('instructor')) return 'faculty_name';
    if (lower.includes('sub category') || lower.includes('sub-category')) return 'sub_category';
    if (lower.includes('category') || lower.includes('business type') || lower.includes('hospital type')) return 'category';
    if (lower.includes('speciality') || lower.includes('specialty')) return 'speciality';
    if (lower.includes('cuisine')) return 'cuisine_type';
    if (lower.includes('veg')) return 'veg_type';
    if (lower.includes('price')) return 'price_level';
    if (lower.includes('dine') || lower.includes('takeaway') || lower.includes('delivery')) return 'dine_in_takeaway_delivery';
    if (lower.includes('dish') || lower.includes('dishes')) return 'popular_dishes';
    if (lower.includes('address')) return 'address';
    if (lower.includes('area') || lower.includes('locality')) return 'area';
    if (lower.includes('city')) return 'city';
    if (lower.includes('country')) return 'country';
    if (lower.includes('pincode') || lower.includes('postcode') || lower.includes('postal')) return 'pincode';
    if (lower.includes('phone') || lower.includes('mobile') || lower.includes('tel') || lower.includes('contact')) return 'phone';
    if (lower.includes('website') || lower.includes('web url')) return 'website';
    if (lower.includes('rating')) return 'rating';
    if (lower.includes('reviews') || lower.includes('review count') || lower.includes('total reviews')) return 'review_count';
    if (lower.includes('opening time') || lower.includes('open time')) return 'opening_time';
    if (lower.includes('closing time') || lower.includes('close time')) return 'closing_time';
    if (lower.includes('full timing') || lower.includes('timing') || lower.includes('hours')) return 'full_timing';
    if (lower.includes('maps url') || lower.includes('google maps') || lower.includes('source url')) return 'source_url';
    if (lower.includes('latitude') || lower === 'lat') return 'latitude';
    if (lower.includes('longitude') || lower === 'lng') return 'longitude';
    if (lower.includes('search pincode') || lower.includes('search postcode')) return 'search_pincode';
    if (lower.includes('search query')) return 'search_query';
    if (lower.includes('scraped')) return 'scraped_at';
    if (lower.includes('name')) return 'name';
    return fieldName.toLowerCase().replace(/[^a-z0-9]+/g, '_');
  };

  const displayFields = useMemo(() => {
    if (selectedFields && selectedFields.length > 0) {
      return selectedFields;
    }
    return ['Name', 'Category', 'Sub Category', 'Address', 'Area', 'City', 'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating', 'Total Reviews', 'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'];
  }, [selectedFields]);

  // Export Duplicates Report to CSV
  const handleExportDuplicatesCsv = () => {
    if (duplicates.length === 0) return;
    const headers = ['Name', 'Category', 'Postal Code', 'City', 'Reason', 'Maps URL', 'Skipped At'];
    const rows = duplicates.map((d) => [
      `"${String(d.name || '').replace(/"/g, '""')}"`,
      `"${String(d.category || '').replace(/"/g, '""')}"`,
      `"${String(d.pincode || d.search_pincode || '').replace(/"/g, '""')}"`,
      `"${String(d.city || '').replace(/"/g, '""')}"`,
      `"${String(d.reason || '').replace(/"/g, '""')}"`,
      `"${String(d.source_url || '').replace(/"/g, '""')}"`,
      `"${String(d.skipped_at || '').replace(/"/g, '""')}"`
    ]);
    const csvContent = '\uFEFF' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `duplicates_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const [copiedPath, setCopiedPath] = useState('');

  const handleCopyPath = (path) => {
    if (!path) return;
    const fallbackCopy = (text) => {
      try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        if (success) {
          setCopiedPath(text);
          setTimeout(() => setCopiedPath(''), 2000);
        }
      } catch (err) {
        console.error('[DataTable] Fallback copy failed:', err);
      }
    };

    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(path).then(() => {
          setCopiedPath(path);
          setTimeout(() => setCopiedPath(''), 2000);
        }).catch(() => fallbackCopy(path));
      } else {
        fallbackCopy(path);
      }
    } catch (_) {
      fallbackCopy(path);
    }
  };

  return (
    <div className="data-table-container app-card">
      {/* 1. Multi-View Tab Navigation Bar */}
      <div className="dataset-tab-nav-bar">
        <button
          type="button"
          className={`dataset-tab-btn ${tab === 'records' ? 'dataset-tab-active dataset-tab-records' : ''}`}
          onClick={() => setTab('records')}
        >
          <CheckCircle2 size={16} />
          <span>Active Dataset</span>
          <span className="dataset-tab-badge badge-active-count">{records.length}</span>
        </button>

        <button
          type="button"
          className={`dataset-tab-btn ${tab === 'duplicates' ? 'dataset-tab-active dataset-tab-duplicates' : ''}`}
          onClick={() => setTab('duplicates')}
        >
          <Copy size={15} />
          <span>Skipped Duplicates</span>
          <span className={`dataset-tab-badge ${duplicates.length > 0 ? 'badge-dup-count' : 'badge-neutral-count'}`}>
            {duplicates.length}
          </span>
        </button>

        <button
          type="button"
          className={`dataset-tab-btn ${tab === 'history' ? 'dataset-tab-active dataset-tab-history' : ''}`}
          onClick={() => {
            setTab('history');
            if (onRefreshHistory) onRefreshHistory();
          }}
        >
          <FolderArchive size={15} />
          <span>Saved CSV History</span>
          <span className="dataset-tab-badge badge-history-count">{historyFiles.length} files</span>
        </button>
      </div>

      {/* VIEW 1: ACTIVE IN-MEMORY DATASET TABLE */}
      {tab === 'records' && (
        <>
          <div className="table-toolbar">
            <div className="table-title-group">
              <h3 className="table-title">Live Scraped Records</h3>
              <span className="table-count-badge">{records.length} records</span>
            </div>

            <div className="table-controls-group">
              <div className="table-search-box">
                <Search size={15} className="table-search-icon" />
                <input
                  type="text"
                  placeholder="Search dataset..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="table-search-input"
                />
              </div>

              <div className="table-download-group">
                {Boolean(defaultCsvFileName || customCsvName) && (
                  <div className="table-filename-input-wrap">
                    <FileSpreadsheet size={14} className="table-filename-icon" />
                    <input
                      type="text"
                      placeholder="CSV filename..."
                      value={customCsvName !== '' ? customCsvName : defaultCsvFileName}
                      onChange={(e) => setCustomCsvName(e.target.value)}
                      title="Enter custom CSV filename to download"
                      className="table-filename-input"
                    />
                  </div>
                )}

                <button
                  type="button"
                  className="btn btn-primary btn-download-csv"
                  onClick={() => onExportCsv(currentExportName)}
                  disabled={records.length === 0}
                >
                  <Download size={15} strokeWidth={2.5} />
                  <span>Download CSV</span>
                </button>
              </div>

              <button
                type="button"
                className="btn btn-outline-danger btn-clear-table"
                onClick={onClearAll}
                disabled={records.length === 0}
                title="Clear in-memory view (CSV file on disk remains safe)"
              >
                <Trash2 size={14} />
                <span>Clear</span>
              </button>
            </div>
          </div>

          <div className="table-scroll-container">
            <table className="dataset-table">
              <thead>
                <tr>
                  <th className="th-index">#</th>
                  {displayFields.map((field) => {
                    const key = getFieldKey(field);
                    return (
                      <th
                        key={field}
                        onClick={() => handleSort(key)}
                        className="th-sortable"
                      >
                        <div className="th-content">
                          <span>{field}</span>
                          <ArrowUpDown size={12} className="th-sort-icon" />
                        </div>
                      </th>
                    );
                  })}
                  <th className="th-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentRecords.length === 0 ? (
                  <tr>
                    <td colSpan={displayFields.length + 2} className="td-empty">
                      {searchTerm
                        ? 'No matching records found in dataset.'
                        : 'No records collected yet. Enter a search query above and click "Start Scraping" or load a saved CSV from the History tab.'}
                    </td>
                  </tr>
                ) : (
                  currentRecords.map((record, index) => {
                    const rowNum = (currentPage - 1) * pageSize + index + 1;
                    return (
                      <tr key={record.id || index} className="dataset-row">
                        <td className="td-index">{rowNum}</td>
                        {displayFields.map((field) => {
                          const key = getFieldKey(field);
                          let rawVal = record[key];
                          if (rawVal === undefined || rawVal === null || rawVal === '' || rawVal === '—') {
                            if (key === 'name') {
                              rawVal = record['Hospital Name'] || record['School Name'] || record['Business Name'] || record['Restaurant Name'] || record['Name'] || record.title;
                              if (!rawVal || rawVal === 'Results' || rawVal === '—') {
                                const mapsUrl = record.source_url || record.google_maps_url || record['Google Maps URL'] || '';
                                if (mapsUrl && mapsUrl.includes('/maps/place/')) {
                                  const m = mapsUrl.match(/\/maps\/place\/([^/@?]+)/);
                                  if (m && m[1]) {
                                    try {
                                      rawVal = decodeURIComponent(m[1].replace(/\+/g, ' '));
                                    } catch (e) {
                                      rawVal = m[1].replace(/\+/g, ' ');
                                    }
                                  }
                                }
                              }
                            }
                            else if (key === 'category') {
                              rawVal = record['Hospital Type'] || record['School Type'] || record['Business Type'] || record['Category'] || record.speciality || record['Speciality'];
                              if (!rawVal || rawVal === 'Business') {
                                const n = String(record.name || record['Hospital Name'] || '').toLowerCase();
                                if (/hospital|eye care|clinic|health care|laser/i.test(n)) rawVal = 'Hospital';
                                else if (/school|academy|college|institute|vidhyalaya/i.test(n)) rawVal = 'School';
                                else if (/restaurant|hotel|cafe|dhaba|dining/i.test(n)) rawVal = 'Restaurant';
                              }
                            }
                            else if (key === 'city') {
                              rawVal = record['City'] || record['town'] || record['Town'];
                              if (!rawVal || rawVal === '—') {
                                const cm = ((record.search_query || record['Search Query'] || '') + ' ' + (record.address || record['Full Address'] || '')).match(/\b(Rajkot|Ahmedabad|Surat|Vadodara|Mumbai|Delhi|Bengaluru|Bangalore|Hyderabad|Chennai|Kolkata|Pune|Jaipur|Indore|Nagpur|Bhavnagar|Jamnagar|Junagadh|Gandhinagar|Anand|Morbi|Surendranagar|Navsari|Vapi|Bharuch|Porbandar|Godhra|Patan|Dahod|Botad|Amreli|Deesa|Jetpur)\b/i);
                                if (cm) rawVal = cm[1].charAt(0).toUpperCase() + cm[1].slice(1).toLowerCase();
                              }
                            }
                            else if (key === 'area') rawVal = record['Area'] || record['locality'] || record['Locality'];
                            else if (key === 'country') rawVal = record['Country'] || 'India';
                            else if (key === 'address') rawVal = record['Full Address'] || record['Address'];
                            else if (key === 'phone') rawVal = record.phone_number || record['Phone Number'] || record['Phone'] || record.mobile;
                            else if (key === 'rating') rawVal = record.google_rating || record['Google Rating'];
                            else if (key === 'review_count') rawVal = record.total_reviews || record['Total Reviews'];
                            else if (key === 'source_url') rawVal = record.google_maps_url || record['Google Maps URL'];
                            else if (key === 'pincode') rawVal = record.pincode_postcode || record['Pincode/Postcode'] || record['Pincode'];
                            else if (key === 'sub_category') rawVal = record.cuisine_type || record.speciality || record['Speciality'] || record['Sub Speciality'];
                            else rawVal = record[field];
                          }
                          const val = (rawVal !== undefined && rawVal !== null && rawVal !== '') ? rawVal : '—';

                          if (key === 'rating') {
                            return (
                              <td key={field} className="td-rating">
                                {val !== '—' ? (
                                  <span className="rating-badge">
                                    <Star size={13} fill="#fbbf24" stroke="#f59e0b" />
                                    <span>{val}</span>
                                  </span>
                                ) : '—'}
                              </td>
                            );
                          }

                          if (key === 'website' && val !== '—' && String(val).startsWith('http')) {
                            return (
                              <td key={field} className="td-link">
                                <a
                                  href={val}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="table-link table-link-website"
                                  title={val}
                                >
                                  <span>Website</span>
                                  <ExternalLink size={11} />
                                </a>
                              </td>
                            );
                          }

                          if (key === 'source_url' && val !== '—' && String(val).startsWith('http')) {
                            return (
                              <td key={field} className="td-link">
                                <a
                                  href={val}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="table-link table-link-maps"
                                  title={val}
                                >
                                  <span>Maps</span>
                                  <ExternalLink size={11} />
                                </a>
                              </td>
                            );
                          }

                          return (
                            <td key={field} className="td-cell-text" title={String(val)}>
                              {String(val)}
                            </td>
                          );
                        })}

                        <td className="td-actions">
                          <div className="table-actions-wrap">
                            {onViewRecord && (
                              <button
                                type="button"
                                className="btn-table-action btn-table-view"
                                onClick={() => onViewRecord(record)}
                                title="View Full Record Details"
                              >
                                <Eye size={14} />
                              </button>
                            )}
                            <button
                              type="button"
                              className="btn-table-action btn-table-edit"
                              onClick={() => onEditRecord(record)}
                              title="Edit Record"
                            >
                              <Edit size={14} />
                            </button>
                            <button
                              type="button"
                              className="btn-table-action btn-table-delete"
                              onClick={() => onDeleteRecord(record)}
                              title="Delete Record"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="table-pagination-footer">
              <span className="pagination-info">
                Showing {Math.min(filteredAndSortedRecords.length, (currentPage - 1) * pageSize + 1)} to{' '}
                {Math.min(filteredAndSortedRecords.length, currentPage * pageSize)} of{' '}
                {filteredAndSortedRecords.length} records
              </span>

              <div className="pagination-controls">
                <button
                  type="button"
                  className="btn btn-outline-neutral btn-sm"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft size={14} />
                  <span>Prev</span>
                </button>

                <span className="pagination-current-page">
                  Page {currentPage} of {totalPages}
                </span>

                <button
                  type="button"
                  className="btn btn-outline-neutral btn-sm"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  <span>Next</span>
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* VIEW 2: SKIPPED DUPLICATES INSPECTOR TABLE */}
      {tab === 'duplicates' && (
        <div className="duplicates-view-container">
          <div className="duplicates-info-banner">
            <div className="banner-icon-wrap">
              <AlertTriangle size={18} />
            </div>
            <div className="banner-text-wrap">
              <h4 className="banner-title">Cross-Postcode Deduplication Inspector</h4>
              <p className="banner-desc">
                Google Maps often returns identical listings for neighboring postal codes or city-wide queries.
                The scraper instantly detected and bypassed these duplicate listings to prevent redundant data.
                You can review every skipped duplicate below or click <strong>Force Include</strong> to add any record to the active dataset.
              </p>
            </div>
          </div>

          <div className="table-toolbar">
            <div className="table-title-group">
              <h3 className="table-title">Skipped Duplicates Log</h3>
              <span className="table-count-badge badge-dup-count">{duplicates.length} skipped</span>
            </div>

            <div className="table-controls-group">
              <div className="table-search-box">
                <Search size={15} className="table-search-icon" />
                <input
                  type="text"
                  placeholder="Search duplicates..."
                  value={dupSearchTerm}
                  onChange={(e) => {
                    setDupSearchTerm(e.target.value);
                    setDupPage(1);
                  }}
                  className="table-search-input"
                />
              </div>

              <button
                type="button"
                className="btn btn-outline-accent btn-sm"
                onClick={handleExportDuplicatesCsv}
                disabled={duplicates.length === 0}
                title="Download duplicates log as CSV"
              >
                <Download size={14} />
                <span>Export Duplicates Log</span>
              </button>

              {onClearDuplicates && (
                <button
                  type="button"
                  className="btn btn-outline-danger btn-sm"
                  onClick={onClearDuplicates}
                  disabled={duplicates.length === 0}
                  title="Clear duplicates list"
                >
                  <Trash2 size={14} />
                  <span>Clear List</span>
                </button>
              )}
            </div>
          </div>

          <div className="table-scroll-container">
            <table className="dataset-table">
              <thead>
                <tr>
                  <th className="th-index">#</th>
                  <th>Business / Hospital Name</th>
                  <th>Category</th>
                  <th>Postal Code / City</th>
                  <th>Deduplication Match Reason</th>
                  <th>Google Maps Link</th>
                  <th>Skipped Time</th>
                  <th className="th-actions">Action</th>
                </tr>
              </thead>
              <tbody>
                {currentDuplicates.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="td-empty">
                      {dupSearchTerm
                        ? 'No matching duplicates found in search.'
                        : 'No duplicates skipped yet. When cross-pincode duplicates are encountered, they will appear here.'}
                    </td>
                  </tr>
                ) : (
                  currentDuplicates.map((dup, index) => {
                    const rowNum = (dupPage - 1) * pageSize + index + 1;
                    return (
                      <tr key={dup.id || index} className="dataset-row row-duplicate">
                        <td className="td-index">{rowNum}</td>
                        <td className="td-cell-text" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {dup.name || 'Unknown Business'}
                        </td>
                        <td className="td-cell-text">{dup.category || 'Business'}</td>
                        <td className="td-cell-text">
                          <span className="badge-postal-pin">
                            {dup.pincode || dup.search_pincode || '—'} {dup.city ? `(${dup.city})` : ''}
                          </span>
                        </td>
                        <td>
                          <span className="badge-dup-reason" title={dup.reason}>
                            {dup.reason || 'Place ID already in saved dataset'}
                          </span>
                        </td>
                        <td className="td-link">
                          {dup.source_url && String(dup.source_url).startsWith('http') ? (
                            <a
                              href={dup.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="table-link table-link-maps"
                            >
                              <span>View Maps</span>
                              <ExternalLink size={11} />
                            </a>
                          ) : '—'}
                        </td>
                        <td className="td-cell-text" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {dup.skipped_at || '—'}
                        </td>
                        <td className="td-actions">
                          <div className="table-actions-wrap">
                            {onViewRecord && (
                              <button
                                type="button"
                                className="btn-table-action btn-table-view"
                                onClick={() => onViewRecord(dup)}
                                title="View Skipped Duplicate Details"
                              >
                                <Eye size={14} />
                              </button>
                            )}
                            {onForceIncludeDuplicate && (
                              <button
                                type="button"
                                className="btn btn-outline-accent btn-sm btn-force-include"
                                onClick={() => onForceIncludeDuplicate(dup)}
                                title="Force include this record in the active dataset"
                              >
                                <PlusCircle size={13} />
                                <span>Include</span>
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {totalDupPages > 1 && (
            <div className="table-pagination-footer">
              <span className="pagination-info">
                Showing {Math.min(filteredDuplicates.length, (dupPage - 1) * pageSize + 1)} to{' '}
                {Math.min(filteredDuplicates.length, dupPage * pageSize)} of{' '}
                {filteredDuplicates.length} duplicates
              </span>

              <div className="pagination-controls">
                <button
                  type="button"
                  className="btn btn-outline-neutral btn-sm"
                  onClick={() => setDupPage((p) => Math.max(1, p - 1))}
                  disabled={dupPage === 1}
                >
                  <ChevronLeft size={14} />
                  <span>Prev</span>
                </button>
                <span className="pagination-current-page">
                  Page {dupPage} of {totalDupPages}
                </span>
                <button
                  type="button"
                  className="btn btn-outline-neutral btn-sm"
                  onClick={() => setDupPage((p) => Math.min(totalDupPages, p + 1))}
                  disabled={dupPage === totalDupPages}
                >
                  <span>Next</span>
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: SAVED CSV HISTORY MANAGER */}
      {tab === 'history' && (
        <div className="history-view-container">
          <div className="history-info-banner">
            <div className="banner-icon-wrap banner-icon-history">
              <FolderArchive size={18} />
            </div>
            <div className="banner-text-wrap">
              <h4 className="banner-title">Saved CSV Datasets on Disk</h4>
              <p className="banner-desc">
                Browse and view all CSV files saved from previous scraping runs. Click <strong>Load into Table View</strong> to inspect, search, filter, edit, or append to any historical dataset.
              </p>
            </div>
          </div>

          <div className="table-toolbar">
            <div className="table-title-group">
              <h3 className="table-title">Available CSV History Files</h3>
              <span className="table-count-badge badge-history-count">{historyFiles.length} files</span>
            </div>

            <div className="table-controls-group">
              <div className="table-search-box">
                <Search size={15} className="table-search-icon" />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={histSearchTerm}
                  onChange={(e) => setHistSearchTerm(e.target.value)}
                  className="table-search-input"
                />
              </div>

              {onRefreshHistory && (
                <button
                  type="button"
                  className="btn btn-outline-neutral btn-sm"
                  onClick={onRefreshHistory}
                  title="Refresh file list from disk"
                >
                  <RotateCw size={14} />
                  <span>Refresh</span>
                </button>
              )}
            </div>
          </div>

          <div className="table-scroll-container">
            <table className="dataset-table">
              <thead>
                <tr>
                  <th className="th-index" style={{ width: '45px' }}>#</th>
                  <th style={{ minWidth: '260px' }}>CSV File Name</th>
                  <th style={{ minWidth: '130px' }}>Records Saved</th>
                  <th style={{ minWidth: '95px' }}>File Size</th>
                  <th style={{ minWidth: '160px' }}>Last Modified</th>
                  <th style={{ minWidth: '320px' }}>Full Disk Location</th>
                  <th className="th-actions" style={{ minWidth: '180px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistoryFiles.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="td-empty">
                      {histSearchTerm
                        ? 'No matching CSV files found.'
                        : 'No saved CSV files found on disk yet.'}
                    </td>
                  </tr>
                ) : (
                  filteredHistoryFiles.map((file, index) => (
                    <tr key={file.filepath || index} className="dataset-row">
                      <td className="td-index">{index + 1}</td>
                      <td className="td-history-filename">
                        <div className="history-filename-cell">
                          <FileSpreadsheet size={16} className="history-file-icon" />
                          <strong className="history-filename-text">{file.filename}</strong>
                        </div>
                      </td>
                      <td className="td-history-badge">
                        <span className="badge-history-records">
                          {file.record_count} records
                        </span>
                      </td>
                      <td className="td-history-meta">
                        {file.size_formatted || `${file.size_bytes} B`}
                      </td>
                      <td className="td-history-meta">
                        <div className="history-time-wrap">
                          <Clock size={13} />
                          <span>{file.modified_at || '—'}</span>
                        </div>
                      </td>
                      <td className="td-history-filepath">
                        <div className="history-path-cell">
                          <span className="history-path-text" title={file.filepath}>
                            {file.filepath}
                          </span>
                          <button
                            type="button"
                            className="btn-copy-path"
                            onClick={() => handleCopyPath(file.filepath)}
                            title="Copy full file path to clipboard"
                          >
                            {copiedPath === file.filepath ? <CheckCircle2 size={13} className="text-success" /> : <Copy size={13} />}
                          </button>
                        </div>
                      </td>
                      <td className="td-actions">
                        <div className="history-actions-wrap">
                          {onLoadHistoryCsv && (
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              onClick={() => onLoadHistoryCsv(file.filepath)}
                              title="Load this CSV file into the active dataset table view"
                            >
                              <FolderOpen size={13} />
                              <span>Load into Table</span>
                            </button>
                          )}
                          {onDeleteHistoryCsv && (
                            <button
                              type="button"
                              className="btn-table-action btn-table-delete"
                              onClick={() => onDeleteHistoryCsv(file)}
                              title="Delete file from disk"
                            >
                              <Trash2 size={15} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
