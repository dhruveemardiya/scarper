import React, { useState, useEffect, useRef, useCallback } from 'react';
import { DatabaseZap, Loader2 } from 'lucide-react';
import Header from './components/Header';
import SearchSection from './components/SearchSection';
import PincodeSelector from './components/PincodeSelector';
import DataFieldsSelector from './components/DataFieldsSelector';
import ProgressHUD from './components/ProgressHUD';
import DataTable from './components/DataTable';
import EditRecordModal from './components/EditRecordModal';
import ViewRecordModal from './components/ViewRecordModal';
import ConfirmDeleteModal from './components/ConfirmDeleteModal';
import ExitConfirmModal from './components/ExitConfirmModal';
import Toast from './components/Toast';
import ScraperBridge from './services/scraperBridge';
import Login from './auth/Login';
import authService from './auth/authService';
import useInactivityTimer from './auth/useInactivityTimer';

const DEFAULT_FIELDS_BY_ENTITY = {
  school: [
    'Name', 'Category', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Affiliation / Board', 'Grades / Classes Offered',
    'Medium of Instruction', 'Principal / Head Name', 'Email Address',
    'Admission Process', 'Annual Fee Range', 'Student-Teacher Ratio',
    'Facilities / Amenities', 'Opening Time', 'Closing Time', 'Full Timing',
    'Google Maps URL'
  ],
  education: [
    'Name', 'Category', 'Courses / Coaching Offered', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Batch Timings', 'Faculty / Instructor Name', 'Fee Structure',
    'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'
  ],
  hospital: [
    'Name', 'Category', 'Speciality', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Emergency Services (24/7)', 'Number of Beds / ICU',
    'Key Doctors / Surgeons', 'Opening Time', 'Closing Time', 'Full Timing',
    'Google Maps URL'
  ],
  restaurant: [
    'Name', 'Category', 'Cuisine Type', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Price Level', 'Dine-in / Takeaway / Delivery', 'Popular Dishes',
    'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'
  ],
  gas_station: [
    'Name', 'Category', 'Fuel Brands', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'EV Charging Available', 'Car Wash Available', 'Convenience Store',
    'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'
  ],
  hotel: [
    'Name', 'Category', 'Star Rating', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Room Types', 'Amenities', 'Check-in / Check-out Time',
    'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'
  ],
  generic: [
    'Name', 'Category', 'Sub Category', 'Address', 'Area', 'City',
    'Country', 'Pincode/Postcode', 'Phone Number', 'Website', 'Google Rating',
    'Total Reviews', 'Opening Time', 'Closing Time', 'Full Timing', 'Google Maps URL'
  ]
};

const normalizeRecord = (r) => {
  if (!r) return r;
  let name = r.name || r['Hospital Name'] || r['School Name'] || r['Business Name'] || r['Restaurant Name'] || r['Institute Name'] || r['College Name'] || r['Clinic Name'] || r['Name'] || r.title || '';
  if (!name || name.toLowerCase() === 'results' || name.toLowerCase() === '—') {
    const mapsUrl = r.source_url || r.google_maps_url || r['Google Maps URL'] || r.url || '';
    if (mapsUrl && mapsUrl.includes('/maps/place/')) {
      const match = mapsUrl.match(/\/maps\/place\/([^/@?]+)/);
      if (match && match[1]) {
        try {
          name = decodeURIComponent(match[1].replace(/\+/g, ' ')).trim();
        } catch (e) {
          name = match[1].replace(/\+/g, ' ').trim();
        }
      }
    }
  }

  let category = r.category || r['Hospital Type'] || r['School Type'] || r['Business Type'] || r['Category'] || r.type || '';
  if (!category || category.toLowerCase() === 'business' || category.toLowerCase() === '—') {
    if (r['Hospital Type']) category = r['Hospital Type'];
    else if (r['School Type']) category = r['School Type'];
    else if (r.speciality || r['Speciality']) category = r.speciality || r['Speciality'];
    else if (name && /hospital|eye care|clinic|health care|laser/i.test(name)) category = 'Hospital';
    else if (name && /school|academy|college|institute|vidhyalaya|classes/i.test(name)) category = 'School';
    else if (name && /restaurant|hotel|cafe|dhaba|dining|food/i.test(name)) category = 'Restaurant';
    else category = category || 'Business';
  }

  const subCategory = r.sub_category || r.speciality || r['Speciality'] || r.sub_speciality || r['Sub Speciality'] || r.cuisine_type || r['Cuisine Type'] || r['Courses / Coaching Offered'] || '';
  
  let city = r.city || r['City'] || r['town'] || r['Town'] || '';
  if (!city || city === '—') {
    const q = r.search_query || r['Search Query'] || '';
    const addr = r.address || r['Full Address'] || r['Address'] || '';
    const cityMatch = (q + ' ' + addr).match(/\b(Rajkot|Ahmedabad|Surat|Vadodara|Mumbai|Delhi|Bengaluru|Bangalore|Hyderabad|Chennai|Kolkata|Pune|Jaipur|Indore|Nagpur|Bhavnagar|Jamnagar|Junagadh|Gandhinagar|Anand|Morbi|Surendranagar|Navsari|Vapi|Bharuch|Porbandar|Godhra|Patan|Dahod|Botad|Amreli|Deesa|Jetpur)\b/i);
    if (cityMatch) {
      city = cityMatch[1].charAt(0).toUpperCase() + cityMatch[1].slice(1).toLowerCase();
    }
  }

  const area = r.area || r['Area'] || r['locality'] || r['Locality'] || '';
  const address = r.address || r['Full Address'] || r['Address'] || '';
  const country = r.country || r['Country'] || 'India';
  const phone = r.phone || r.phone_number || r['Phone Number'] || r['Phone'] || r.mobile || '';
  const website = r.website || r['Website'] || '';
  const rating = (r.rating !== undefined && r.rating !== null && r.rating !== '' && r.rating !== '—') ? r.rating : (r.google_rating || r['Google Rating'] || null);
  const reviewCount = (r.review_count !== undefined && r.review_count !== null && r.review_count !== '' && r.review_count !== '—') ? r.review_count : (r.total_reviews || r['Total Reviews'] || null);
  const fullTiming = r.full_timing || r['Full Timing'] || r.timing_str || r.Timing || '';
  const openingTime = r.opening_time || r['Opening Time'] || '';
  const closingTime = r.closing_time || r['Closing Time'] || '';
  const sourceUrl = r.source_url || r.google_maps_url || r['Google Maps URL'] || '';
  const pincode = r.pincode || r.pincode_postcode || r['Pincode/Postcode'] || r['Pincode'] || r.search_pincode || '';

  return {
    ...r,
    name,
    category,
    sub_category: subCategory,
    city,
    area,
    address,
    country,
    phone,
    phone_number: phone,
    website,
    rating,
    google_rating: rating,
    review_count: reviewCount,
    total_reviews: reviewCount,
    full_timing: fullTiming,
    opening_time: openingTime,
    closing_time: closingTime,
    source_url: sourceUrl,
    google_maps_url: sourceUrl,
    pincode,
    pincode_postcode: pincode
  };
};

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [isConnected, setIsConnected] = useState(false);
  const [toasts, setToasts] = useState([]);

  // Authentication & Session States
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);
  const [authErrorMessage, setAuthErrorMessage] = useState('');

  // Search & NLP State (Starts completely empty on initial load)
  const [searchQuery, setSearchQuery] = useState('');
  const [parsedInfo, setParsedInfo] = useState(null);

  // Postal Codes State (Hidden on initial load, revealed only upon execution/resolution)
  const [pincodeSectionVisible, setPincodeSectionVisible] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  const [availablePincodes, setAvailablePincodes] = useState([]);
  const [selectedPincodes, setSelectedPincodes] = useState([]);
  const [postalLabel, setPostalLabel] = useState('Pincode');

  // Dynamic Data Fields State
  const [selectedFields, setSelectedFields] = useState([]);
  const [customFields, setCustomFields] = useState([]);

  // Scraping Execution & Queue State
  const [outputCsvPath, setOutputCsvPath] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [pincodeQueue, setPincodeQueue] = useState([]);
  const [pincodeStatuses, setPincodeStatuses] = useState({});
  const [currentListingInfo, setCurrentListingInfo] = useState(null);

  // In-Memory Dataset (Directly synced with CSV)
  const [records, setRecords] = useState([]);
  const [duplicates, setDuplicates] = useState([]);
  const [historyFiles, setHistoryFiles] = useState([]);
  const [activeTableTab, setActiveTableTab] = useState('records');
  const [stats, setStats] = useState({
    found: 0,
    collected: 0,
    duplicates: 0,
    failed: 0,
    progress_pct: 0,
    current_pincode: '',
    pincode_index: 0,
    pincode_total: 0
  });

  // Modal States
  const [editingRecord, setEditingRecord] = useState(null);
  const [viewingRecord, setViewingRecord] = useState(null);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [fileToDelete, setFileToDelete] = useState(null);
  const [clearTableConfirmOpen, setClearTableConfirmOpen] = useState(false);
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false);

  const debounceTimer = useRef(null);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  }, []);

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const refreshHistoryFiles = useCallback(async () => {
    try {
      const res = await ScraperBridge.getHistory();
      if (res && res.files) {
        setHistoryFiles(res.files);
      }
    } catch (err) {
      console.error('[App] Failed to fetch history files:', err);
    }
  }, []);

  // Get recommended fields based on detected entity
  const getEntityFields = useCallback((entityType) => {
    const ent = (entityType || 'generic').toLowerCase();
    if (ent.includes('school')) return DEFAULT_FIELDS_BY_ENTITY.school;
    if (ent.includes('college') || ent.includes('institute') || ent.includes('coaching') || ent.includes('classes') || ent.includes('tuition') || ent.includes('education')) return DEFAULT_FIELDS_BY_ENTITY.education;
    if (ent.includes('hospital') || ent.includes('clinic') || ent.includes('doctor') || ent.includes('dental')) return DEFAULT_FIELDS_BY_ENTITY.hospital;
    if (ent.includes('restaurant') || ent.includes('cafe') || ent.includes('food') || ent.includes('dining') || ent.includes('dhaba')) return DEFAULT_FIELDS_BY_ENTITY.restaurant;
    if (ent.includes('gas_station') || ent.includes('petrol') || ent.includes('fuel')) return DEFAULT_FIELDS_BY_ENTITY.gas_station;
    if (ent.includes('hotel') || ent.includes('resort') || ent.includes('lodge')) return DEFAULT_FIELDS_BY_ENTITY.hotel;
    return DEFAULT_FIELDS_BY_ENTITY.generic;
  }, []);

  // Generate Dynamic Default CSV Filename based on Search Query
  const generateDefaultCsvFilename = (parsed) => {
    const city = parsed?.city || 'business';
    const area = parsed?.area ? `_${parsed.area}` : '';
    const entity = parsed?.entity_label || parsed?.entity_type || 'records';
    const date = new Date().toISOString().slice(0, 10);
    const cleanCity = city.replace(/[^a-zA-Z0-9_-]/g, '_');
    const cleanArea = area.replace(/[^a-zA-Z0-9_-]/g, '_');
    const cleanEntity = entity.replace(/[^a-zA-Z0-9_-]/g, '_');
    return `${cleanCity}${cleanArea}_${cleanEntity}_${date}.csv`;
  };

  // Query Input Change Handler (Directly resolves pincodes, displays Pincode Section & + Add Pincode button)
  const handleQueryChange = (newVal, immediate = false) => {
    setSearchQuery(newVal);

    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    const trimmed = newVal.trim();

    if (!trimmed) {
      setParsedInfo(null);
      setOutputCsvPath('');
      setPincodeSectionVisible(false);
      setAvailablePincodes([]);
      setSelectedPincodes([]);
      setIsResolving(false);
      return;
    }

    // For 1-2 characters, do not show resolving indicator yet; allow fluid typing
    if (trimmed.length < 3) {
      setParsedInfo(null);
      setIsResolving(false);
      return;
    }

    const executeParse = async () => {
      setIsResolving(true);
      try {
        const res = await ScraperBridge.parseQuery(trimmed);
        if (res && res.parsed) {
          setParsedInfo(res.parsed);
          const pLabel = res.parsed.postal_label || (res.parsed.country === 'UK' ? 'Postcode' : 'Pincode');
          setPostalLabel(pLabel);

          const resolved = res.parsed.resolved_pincodes || [];
          setAvailablePincodes(resolved);
          setSelectedPincodes(resolved);
          setPincodeSectionVisible(true);

          // Update default fields for detected entity
          const recFields = getEntityFields(res.parsed.entity_type);
          setSelectedFields([...recFields, ...customFields]);

          // Update default CSV filename suggestion
          const defName = generateDefaultCsvFilename(res.parsed);
          setOutputCsvPath(defName);
        }
      } catch (err) {
        console.error('[App] Failed to parse query and resolve pincodes:', err);
      } finally {
        setIsResolving(false);
      }
    };

    if (immediate) {
      executeParse();
    } else {
      debounceTimer.current = setTimeout(executeParse, 280);
    }
  };

  // Pincode Selection Handlers
  const handleTogglePincode = (pin) => {
    setSelectedPincodes((prev) =>
      prev.includes(pin) ? prev.filter((p) => p !== pin) : [...prev, pin]
    );
  };

  const handleSelectAllPincodes = () => {
    setSelectedPincodes([...availablePincodes]);
  };

  const handleClearAllPincodes = () => {
    setSelectedPincodes([]);
  };

  const handleAddCustomPincode = (newPin) => {
    if (!availablePincodes.includes(newPin)) {
      setAvailablePincodes((prev) => [newPin, ...prev]);
    }
    if (!selectedPincodes.includes(newPin)) {
      setSelectedPincodes((prev) => [newPin, ...prev]);
      addToast(`Added ${newPin} to ${postalLabel} list.`, 'info');
    }
  };

  // Data Field Handlers
  const handleToggleField = (field) => {
    setSelectedFields((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field]
    );
  };

  const handleSelectAllFields = () => {
    const recFields = getEntityFields(parsedInfo?.entity_type);
    setSelectedFields([...recFields, ...customFields]);
  };

  const handleClearAllFields = () => {
    setSelectedFields([]);
  };

  const handleAddCustomField = (fieldName) => {
    const clean = fieldName.trim();
    if (clean && !customFields.includes(clean)) {
      setCustomFields((prev) => [...prev, clean]);
      setSelectedFields((prev) => [...prev, clean]);
      addToast(`Added custom field: "${clean}"`, 'success');
    }
  };

  // Save CSV File Location Dialog
  const handleChooseCsvPath = async () => {
    const defName = outputCsvPath || generateDefaultCsvFilename(parsedInfo);
    try {
      const res = await ScraperBridge.showSaveDialog(defName);
      if (!res.canceled && res.filePath) {
        setOutputCsvPath(res.filePath);
        addToast(`CSV save path set to: ${res.filePath}`, 'success');
      }
    } catch (err) {
      console.error('[App] Save dialog error:', err);
    }
  };

  // Load Historical CSV File Handler
  const handleLoadHistoryCsv = async (filePath) => {
    try {
      const fileName = filePath.split(/[\\/]/).pop();
      addToast(`Loading ${fileName}...`, 'info');
      const res = await ScraperBridge.loadCsv(filePath);
      if (res.success && res.records) {
        // Robust client-side record normalizer to guarantee no missing fields
        const normalizedList = res.records.map((r) => {
          const name = r.name || r['Hospital Name'] || r['School Name'] || r['Business Name'] || r['Restaurant Name'] || r['Institute Name'] || r['College Name'] || r['Clinic Name'] || r['Name'] || r.title || '';
          const category = r.category || r['Hospital Type'] || r['School Type'] || r['Business Type'] || r['Category'] || r.type || 'Business';
          const subCategory = r.sub_category || r.speciality || r['Speciality'] || r.sub_speciality || r['Sub Speciality'] || r.cuisine_type || r['Cuisine Type'] || '';
          const city = r.city || r['City'] || r['town'] || r['Town'] || '';
          const area = r.area || r['Area'] || r['locality'] || r['Locality'] || '';
          const address = r.address || r['Full Address'] || r['Address'] || '';
          const country = r.country || r['Country'] || 'India';
          const phone = r.phone || r.phone_number || r['Phone Number'] || r['Phone'] || r.mobile || '';
          const website = r.website || r['Website'] || '';
          const rating = (r.rating !== undefined && r.rating !== null && r.rating !== '') ? r.rating : (r.google_rating || r['Google Rating'] || null);
          const reviewCount = (r.review_count !== undefined && r.review_count !== null && r.review_count !== '') ? r.review_count : (r.total_reviews || r['Total Reviews'] || null);
          const fullTiming = r.full_timing || r['Full Timing'] || r.timing_str || r.Timing || '';
          const openingTime = r.opening_time || r['Opening Time'] || '';
          const closingTime = r.closing_time || r['Closing Time'] || '';
          const sourceUrl = r.source_url || r.google_maps_url || r['Google Maps URL'] || '';
          const pincode = r.pincode || r.pincode_postcode || r['Pincode/Postcode'] || r['Pincode'] || r.search_pincode || '';

          return {
            ...r,
            name,
            category,
            sub_category: subCategory,
            city,
            area,
            address,
            country,
            phone,
            phone_number: phone,
            website,
            rating,
            google_rating: rating,
            review_count: reviewCount,
            total_reviews: reviewCount,
            full_timing: fullTiming,
            opening_time: openingTime,
            closing_time: closingTime,
            source_url: sourceUrl,
            google_maps_url: sourceUrl,
            pincode,
            pincode_postcode: pincode
          };
        });

        // Auto-adapt table columns for loaded entity type
        const lowerName = fileName.toLowerCase();
        let detectedType = 'generic';
        if (lowerName.includes('hospital') || lowerName.includes('clinic') || lowerName.includes('doctor')) {
          detectedType = 'hospital';
        } else if (lowerName.includes('school') || lowerName.includes('college') || lowerName.includes('coaching')) {
          detectedType = 'school';
        } else if (lowerName.includes('restaurant') || lowerName.includes('food') || lowerName.includes('cafe')) {
          detectedType = 'restaurant';
        }
        const entityFields = getEntityFields(detectedType);
        setSelectedFields(entityFields);

        setRecords(normalizedList);
        setOutputCsvPath(res.filepath);
        setStats({
          found: normalizedList.length,
          collected: normalizedList.length,
          duplicates: 0,
          failed: 0,
          progress_pct: 100,
          current_pincode: '',
          pincode_index: 0,
          pincode_total: 0
        });
        setActiveTableTab('records');
        addToast(`Loaded ${normalizedList.length} historical records into dataset view!`, 'success');
      } else {
        addToast(`Failed to load CSV: ${res.error || 'Unknown error'}`, 'error');
      }
    } catch (err) {
      console.error('[App] Error loading CSV history:', err);
      addToast(`Error loading CSV: ${err.message}`, 'error');
    }
  };

  // Delete Historical CSV File Handler (triggers SweetAlert)
  const handleDeleteHistoryCsv = (fileOrPath) => {
    const fileObj = (fileOrPath && typeof fileOrPath === 'object')
      ? fileOrPath
      : { filepath: fileOrPath, filename: String(fileOrPath).split(/[\\/]/).pop() };
    setFileToDelete(fileObj);
  };

  const handleConfirmDeleteHistoryCsv = async (fileObj) => {
    if (!fileObj || !fileObj.filepath) return;
    try {
      const res = await ScraperBridge.deleteCsv(fileObj.filepath);
      if (res.success) {
        setFileToDelete(null);
        addToast(`Deleted "${fileObj.filename || fileObj.filepath}" from disk.`, 'success');
        refreshHistoryFiles();
      } else {
        addToast(`Could not delete file: ${res.error || 'Unknown error'}`, 'error');
      }
    } catch (err) {
      console.error('[App] Error deleting CSV history:', err);
      addToast(`Error deleting file: ${err.message}`, 'error');
    }
  };

  // Force-Include a Skipped Duplicate
  const handleForceIncludeDuplicate = (dupRecord) => {
    setDuplicates((prev) => prev.filter((d) => d.id !== dupRecord.id));
    const rec = {
      ...dupRecord,
      status: 'Force Included'
    };
    setRecords((prev) => [rec, ...prev]);
    setStats((prev) => ({
      ...prev,
      collected: prev.collected + 1,
      duplicates: Math.max(0, prev.duplicates - 1)
    }));
    addToast(`"${dupRecord.name}" added to active records!`, 'success');
  };

  const handleClearDuplicates = () => {
    setDuplicates([]);
    addToast('Duplicates list cleared.', 'info');
  };

  // Synchronize with authoritative Python server state
  const applyServerState = useCallback((st) => {
    if (!st) return;
    setIsConnected(true);
    if (st.status === 'scraping') {
      setIsScraping(true);
      setPincodeSectionVisible(true);
      if (st.search_query) setSearchQuery(st.search_query);
      if (st.parsed_info && Object.keys(st.parsed_info).length > 0) setParsedInfo(st.parsed_info);
      if (st.pincode_queue && st.pincode_queue.length > 0) {
        setPincodeQueue(st.pincode_queue);
        setAvailablePincodes(st.pincode_queue);
        setSelectedPincodes(st.pincode_queue);
      }
      if (st.pincode_statuses) setPincodeStatuses(st.pincode_statuses);
      if (st.current_listing_info) setCurrentListingInfo(st.current_listing_info);
      if (st.stats) setStats(st.stats);
      if (st.records && st.records.length > 0) setRecords(st.records.map(normalizeRecord));
      if (st.duplicates && st.duplicates.length > 0) setDuplicates(st.duplicates);
      if (st.output_csv_path) setOutputCsvPath(st.output_csv_path);
      if (st.status_message) setStatusMessage(st.status_message);
    } else if (st.status === 'completed' || st.status === 'stopped') {
      setIsScraping(false);
      if (st.stats) setStats(st.stats);
      if (st.records && st.records.length > 0) setRecords(st.records.map(normalizeRecord));
      if (st.duplicates) setDuplicates(st.duplicates);
    } else if (st.status === 'idle' || st.status === 'cleared') {
      setIsScraping(false);
      setRecords((st.records || []).map(normalizeRecord));
      setDuplicates(st.duplicates || []);
      setPincodeQueue(st.pincode_queue || []);
      setPincodeStatuses(st.pincode_statuses || {});
      setCurrentListingInfo(st.current_listing_info || null);
      setStatusMessage(st.status_message || '');
      if (st.stats) setStats(st.stats);
    }
  }, []);

  // Initialize Auth & Session Expiration Handlers
  useEffect(() => {
    authService.setSessionExpiredHandler((reason) => {
      setIsAuthenticated(false);
      setCurrentUser(null);
      setAuthErrorMessage(
        reason === 'session_expired'
          ? 'Your session has expired due to inactivity. Please login again.'
          : 'Please sign in to access the application.'
      );
      ScraperBridge.closeWebSocket();
    });

    const verifyExistingSession = async () => {
      setIsAuthChecking(true);
      try {
        const res = await authService.verifySession();
        if (res.authenticated) {
          setIsAuthenticated(true);
          setCurrentUser(res.user);
          setAuthErrorMessage('');
          ScraperBridge.reconnectWebSocket();
        } else {
          setIsAuthenticated(false);
          setCurrentUser(null);
        }
      } catch (_) {
        setIsAuthenticated(false);
        setCurrentUser(null);
      } finally {
        setIsAuthChecking(false);
      }
    };

    verifyExistingSession();
  }, []);

  // 2-Hour User Inactivity Timer
  useInactivityTimer({
    isAuthenticated,
    timeoutSeconds: currentUser?.session_timeout || 7200,
    onSessionExpired: (msg) => {
      setIsAuthenticated(false);
      setCurrentUser(null);
      setAuthErrorMessage(msg);
      ScraperBridge.closeWebSocket();
    }
  });

  const handleLoginSuccess = (user) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
    setAuthErrorMessage('');
    ScraperBridge.reconnectWebSocket();
    refreshHistoryFiles();
    ScraperBridge.getState()
      .then((st) => {
        if (st) applyServerState(st);
      })
      .catch(() => {});
    ScraperBridge.ping()
      .then((res) => {
        if (res && res.status === 'ok') setIsConnected(true);
      })
      .catch(() => setIsConnected(false));
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setAuthErrorMessage('');
    ScraperBridge.closeWebSocket();
  };

  // Initialize Connection & Python Event Listeners
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    if (!isAuthenticated) return;

    refreshHistoryFiles();

    // Initial state check
    ScraperBridge.getState()
      .then((st) => {
        if (st) {
          applyServerState(st);
        }
      })
      .catch((err) => {
        console.error('[App] State check error:', err);
      });

    ScraperBridge.ping()
      .then((res) => {
        if (res && res.status === 'ok') {
          setIsConnected(true);
        }
      })
      .catch(() => {
        setIsConnected(false);
      });

    const unsubscribeEvents = ScraperBridge.onScraperEvent((eventData) => {
      const { event, data, server_state } = eventData || {};

      if (server_state) {
        applyServerState(server_state);
      }

      if (event === 'INIT_STATE') {
        applyServerState(data);
      } else if (event === 'connected') {
        setIsConnected(true);
        refreshHistoryFiles();
      } else if (event === 'ready') {
        setIsConnected(true);
        refreshHistoryFiles();
        addToast('Scraper Engine connected and ready.', 'success');
      } else if (event === 'pincode_start') {
        const pin = data.pincode;
        setPincodeStatuses((prev) => ({ ...prev, [pin]: 'scraping' }));
        setStatusMessage(`Scraping Google Maps for ${postalLabel} ${pin} (${data.index} of ${data.total})...`);
        if (data.stats) setStats(data.stats);
      } else if (event === 'pincode_complete') {
        const pin = data.pincode;
        setPincodeStatuses((prev) => ({ ...prev, [pin]: 'completed' }));
        if (data.stats) setStats(data.stats);
        refreshHistoryFiles();
      } else if (event === 'pincode_failed') {
        const pin = data.pincode;
        setPincodeStatuses((prev) => ({ ...prev, [pin]: 'failed' }));
        if (data.stats) setStats(data.stats);
        addToast(`Failed to scrape ${postalLabel} ${pin}. Continuing to next...`, 'error');
      } else if (event === 'listing_progress') {
        setCurrentListingInfo({
          index: data.listing_index,
          total: data.listing_total,
          label: data.label
        });
      } else if (event === 'record') {
        const newRecord = normalizeRecord(data.record);
        setRecords((prev) => {
          if (prev.some((r) => r.id === newRecord.id || (r.name === newRecord.name && r.phone && r.phone === newRecord.phone))) {
            return prev;
          }
          return [newRecord, ...prev];
        });
      } else if (event === 'duplicate') {
        if (data.record) {
          setDuplicates((prev) => {
            if (prev.some((d) => d.id === data.record.id || (d.name === data.record.name && d.source_url === data.record.source_url))) {
              return prev;
            }
            return [data.record, ...prev];
          });
        }
        if (data.stats) setStats(data.stats);
      } else if (event === 'status') {
        if (data.stats) setStats(data.stats);
        if (data.status === 'completed') {
          setIsScraping(false);
          setStatusMessage(`Completed! All records immediately saved to CSV.`);
          addToast(`Scraping finished. All records saved to CSV file.`, 'success');
          refreshHistoryFiles();
          const targetCsv = data.output_csv || outputCsvPath;
          if (targetCsv) {
            ScraperBridge.loadCsv(targetCsv).then((res) => {
              if (res && res.success && res.records && res.records.length > 0) {
                setRecords(res.records.map(normalizeRecord));
                setStats((prev) => ({
                  ...prev,
                  collected: res.records.length,
                  found: res.records.length,
                  progress_pct: 100
                }));
              }
            }).catch(() => {});
          }
        } else if (data.status === 'stopped') {
          setIsScraping(false);
          setStatusMessage('Scraping stopped by user.');
          addToast('Scraping stopped. Partial records remain saved in CSV.', 'info');
          refreshHistoryFiles();
        } else if (data.status === 'cleared') {
          setIsScraping(false);
          setRecords([]);
          setDuplicates([]);
          setPincodeQueue([]);
          setPincodeStatuses({});
          setCurrentListingInfo(null);
          setStatusMessage('');
          setStats({
            found: 0,
            collected: 0,
            duplicates: 0,
            failed: 0,
            progress_pct: 0,
            current_pincode: '',
            pincode_index: 0,
            pincode_total: 0
          });
        } else if (data.status === 'csv_loaded') {
          refreshHistoryFiles();
        }
      } else if (event === 'error') {
        setIsScraping(false);
        addToast(`Scraper error: ${data.error || 'Unknown error'}`, 'error');
      }
    });

    ScraperBridge.onAppClosing(() => {
      if (records.length > 0) {
        setExitConfirmOpen(true);
      } else {
        ScraperBridge.respondToClosing(true);
      }
    });

    return () => {
      if (typeof unsubscribeEvents === 'function') unsubscribeEvents();
    };
  }, [records.length, postalLabel, applyServerState, refreshHistoryFiles]);

  // Start Sequential Pincode Scraping Queue
  const handleStartScraping = async () => {
    if (isScraping || isResolving) return;

    const trimmedQuery = searchQuery.trim();
    if (!trimmedQuery) {
      addToast('Please enter a search query (e.g. school in Ahmedabad).', 'error');
      return;
    }

    let currentParsed = parsedInfo;
    let currentPincodes = selectedPincodes;
    let currentAvailable = availablePincodes;

    // Step 1: If pincode section is not yet visible or availablePincodes is empty, resolve query now
    if (!pincodeSectionVisible || currentAvailable.length === 0) {
      setIsResolving(true);
      setStatusMessage('Resolving search query & finding postal codes...');

      try {
        const res = await ScraperBridge.parseQuery(trimmedQuery);
        if (res && res.parsed) {
          currentParsed = res.parsed;
          setParsedInfo(res.parsed);

          const pLabel = res.parsed.postal_label || (res.parsed.country === 'UK' ? 'Postcode' : 'Pincode');
          setPostalLabel(pLabel);

          const resolved = res.parsed.resolved_pincodes || [];
          currentAvailable = resolved;
          currentPincodes = resolved;
          setAvailablePincodes(resolved);
          setSelectedPincodes(resolved);
          setPincodeSectionVisible(true);

          // Update default fields for detected entity
          const recFields = getEntityFields(res.parsed.entity_type);
          setSelectedFields([...recFields, ...customFields]);

          // Update default CSV filename suggestion
          const defName = generateDefaultCsvFilename(res.parsed);
          setOutputCsvPath(defName);

          if (resolved.length === 0) {
            setIsResolving(false);
            addToast(`No automatic ${pLabel.toLowerCase()}s found for this location. You can manually enter one below.`, 'info');
            return;
          }
        } else {
          setIsResolving(false);
          addToast('Could not resolve location for query.', 'error');
          return;
        }
      } catch (err) {
        console.error('[App] Query resolution failed:', err);
        setIsResolving(false);
        addToast(`Query resolution error: ${err.message}`, 'error');
        return;
      } finally {
        setIsResolving(false);
      }
    }

    // Step 2: Ensure at least one postal code is selected
    if (currentPincodes.length === 0) {
      addToast(`Please select or add at least one ${postalLabel}.`, 'error');
      return;
    }

    // Step 3: Choose/Validate CSV Save Path
    let targetPath = outputCsvPath;
    if (!targetPath || !targetPath.includes('.')) {
      const defName = generateDefaultCsvFilename(currentParsed);
      const saveRes = await ScraperBridge.showSaveDialog(defName);
      if (saveRes.canceled || !saveRes.filePath) {
        addToast('Please choose a valid CSV file to start scraping.', 'info');
        return;
      }
      targetPath = saveRes.filePath;
      setOutputCsvPath(targetPath);
    }

    // Step 4: Initialize Scraping Run
    setIsScraping(true);
    setPincodeQueue(currentPincodes);
    const initialStatuses = {};
    currentPincodes.forEach((p) => {
      initialStatuses[p] = 'pending';
    });
    setPincodeStatuses(initialStatuses);
    setStatusMessage(`Starting ${currentPincodes.length} ${postalLabel}s queue...`);
    setStats({
      found: 0,
      collected: records.length,
      duplicates: 0,
      failed: 0,
      progress_pct: 0,
      current_pincode: currentPincodes[0] || '',
      pincode_index: 0,
      pincode_total: currentPincodes.length
    });

    try {
      const entity = currentParsed?.entity_type || 'business';
      const entityLabel = currentParsed?.entity_label || entity;
      const city = currentParsed?.city || '';
      const area = currentParsed?.area || '';
      const country = currentParsed?.country || 'India';

      // Build sequential queue
      const queue = currentPincodes.map((pin) => ({
        raw_query: trimmedQuery,
        entity_type: entity,
        entity_label: entityLabel,
        country: country,
        city: city,
        area: area,
        pincode: pin,
        speciality: currentParsed?.speciality || '',
        keyword: currentParsed?.keyword || ''
      }));

      setActiveTableTab('records');

      await ScraperBridge.startScraping({
        queue,
        outputCsvPath: targetPath,
        existingRecords: records,
        customFields: customFields
      });

      addToast(`Started queue scraping for ${currentPincodes.length} ${postalLabel}s.`, 'info');
    } catch (err) {
      console.error('[App] Failed to start scraping queue:', err);
      setIsScraping(false);
      addToast(`Failed to launch scraper: ${err.message}`, 'error');
    }
  };

  // Stop Scraping Action
  const handleStopScraping = async () => {
    try {
      await ScraperBridge.stopScraping();
      setIsScraping(false);
      setStatusMessage('Scraping halted.');
      addToast('Scraping halted. All existing records remain saved in CSV.', 'info');
    } catch (err) {
      console.error('[App] Error stopping scraper:', err);
    }
  };

  // Direct CSV Export Action
  const handleExportCsv = async (overrideFilename) => {
    if (records.length === 0) {
      addToast('No in-memory records to export.', 'error');
      return;
    }
    const targetName = (typeof overrideFilename === 'string' && overrideFilename.trim())
      ? overrideFilename.trim()
      : (outputCsvPath || generateDefaultCsvFilename(parsedInfo));

    try {
      const res = await ScraperBridge.exportCsv(records, targetName, parsedInfo?.entity_type || 'business');
      if (res.success) {
        addToast(`CSV exported successfully to: ${res.file_path}`, 'success');
        refreshHistoryFiles();
      } else if (!res.canceled) {
        addToast(`CSV export failed: ${res.error || 'Unknown error'}`, 'error');
      }
    } catch (err) {
      console.error('[App] CSV export error:', err);
      addToast('Error generating CSV export', 'error');
    }
  };

  // Manual Record Handlers
  const handleSaveEditedRecord = (updatedRecord) => {
    setRecords((prev) => prev.map((r) => (r.id === updatedRecord.id ? updatedRecord : r)));
    addToast(`Record for "${updatedRecord.name}" updated successfully.`, 'success');
  };

  const handleDeleteRecord = (record) => {
    setRecordToDelete(record);
  };

  const handleConfirmDelete = (record) => {
    if (!record) return;
    const targetId = record.id;
    if (targetId) {
      setRecords((prev) => prev.filter((r) => r.id !== targetId));
    } else {
      setRecords((prev) => prev.filter((r) => r !== record));
    }
    const name = record.name || record['Business Name'] || record['Hospital Name'] || record['School Name'] || 'Record';
    setRecordToDelete(null);
    addToast(`"${name}" deleted successfully.`, 'success');
  };

  const handleClearAll = () => {
    if (records.length === 0) {
      addToast('Table view is already empty.', 'info');
      return;
    }
    setClearTableConfirmOpen(true);
  };

  const handleConfirmClearAll = async () => {
    setRecords([]);
    setDuplicates([]);
    setPincodeQueue([]);
    setPincodeStatuses({});
    setCurrentListingInfo(null);
    setStatusMessage('');
    setOutputCsvPath('');
    setStats({
      found: 0,
      collected: 0,
      duplicates: 0,
      failed: 0,
      progress_pct: 0,
      current_pincode: '',
      pincode_index: 0,
      pincode_total: 0
    });
    setClearTableConfirmOpen(false);
    addToast('Active dataset view cleared.', 'info');
    try {
      await ScraperBridge.clearState();
    } catch (err) {
      console.error('[App] Failed to clear server state:', err);
    }
  };

  const handleDownloadAndExit = async () => {
    await handleExportCsv();
    setExitConfirmOpen(false);
    ScraperBridge.respondToClosing(true);
  };

  const handleExitWithoutSaving = () => {
    setExitConfirmOpen(false);
    ScraperBridge.respondToClosing(true);
  };

  if (isAuthChecking) {
    return (
      <div className="auth-loading-screen">
        <div className="auth-loading-card">
          <div className="login-logo-icon">
            <DatabaseZap size={32} />
          </div>
          <h3>Verifying Security Session...</h3>
          <Loader2 size={24} className="auth-spinner" style={{ color: 'var(--accent, #f97316)' }} />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Login
        theme={theme}
        toggleTheme={toggleTheme}
        onLoginSuccess={handleLoginSuccess}
        initialError={authErrorMessage}
      />
    );
  }

  return (
    <div className="app-container" style={{ width: '100%', minHeight: '100vh', padding: '16px 24px', boxSizing: 'border-box' }}>
      {/* Header */}
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        inMemoryCount={records.length}
        duplicateCount={duplicates.length}
        historyCount={historyFiles.length}
        isConnected={isConnected}
        onSelectTab={(t) => setActiveTableTab(t)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {!ScraperBridge.isAvailable() && (
        <div style={{
          padding: '12px 18px',
          marginBottom: '16px',
          background: 'rgba(245, 158, 11, 0.12)',
          border: '1px solid rgba(245, 158, 11, 0.35)',
          borderRadius: '10px',
          color: '#f59e0b',
          fontSize: '13.5px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span>💡 <strong>Browser Mode:</strong> You are viewing in an external web browser. To launch live Selenium Google Maps scraping and direct CSV writing, please use the desktop Electron application window.</span>
        </div>
      )}

      {/* 1. Main Search & Parameter Bar */}
      <SearchSection
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onQueryChange={handleQueryChange}
        parsedInfo={parsedInfo}
        outputCsvPath={outputCsvPath}
        onChooseCsvPath={handleChooseCsvPath}
        onStartScraping={handleStartScraping}
        onStopScraping={handleStopScraping}
        isScraping={isScraping}
        isResolving={isResolving}
        selectedPincodesCount={selectedPincodes.length}
      />

      {/* 2. City -> Pincode Resolution & Multi-Selector (Only shown after user enters query) */}
      {pincodeSectionVisible && (
        <PincodeSelector
          city={parsedInfo?.city}
          postalLabel={postalLabel}
          pincodes={availablePincodes}
          selectedPincodes={selectedPincodes}
          onTogglePincode={handleTogglePincode}
          onSelectAll={handleSelectAllPincodes}
          onClearAll={handleClearAllPincodes}
          onAddCustomPincode={handleAddCustomPincode}
          isScraping={isScraping}
          isResolving={isResolving}
        />
      )}

      {/* 3. Data Fields Configuration & Custom Fields (Shown when pincodes are resolved or scraping) */}
      {(pincodeSectionVisible || isScraping || records.length > 0) && (
        <DataFieldsSelector
          entityType={parsedInfo?.entity_type}
          entityLabel={parsedInfo?.entity_label || parsedInfo?.entity_type}
          availableFields={getEntityFields(parsedInfo?.entity_type)}
          selectedFields={selectedFields}
          onToggleField={handleToggleField}
          onSelectAllFields={handleSelectAllFields}
          onClearAllFields={handleClearAllFields}
          onAddCustomField={handleAddCustomField}
          customFields={customFields}
          isScraping={isScraping}
          onStartScraping={handleStartScraping}
          onStopScraping={handleStopScraping}
          isResolving={isResolving}
          selectedPincodesCount={selectedPincodes.length}
        />
      )}

      {/* 4. Sequential Pincode Queue Progress HUD (Visible only during active scrape or with active dataset) */}
      {(isScraping || ((records.length > 0 || duplicates.length > 0) && (stats.pincode_total > 0 || stats.collected > 0))) && (
        <ProgressHUD
          stats={stats}
          isScraping={isScraping}
          statusMessage={statusMessage}
          onStopScraping={handleStopScraping}
          pincodeQueue={pincodeQueue.length > 0 ? pincodeQueue : selectedPincodes}
          pincodeStatuses={pincodeStatuses}
          currentListingInfo={currentListingInfo}
          outputCsvPath={outputCsvPath}
          onSelectTab={(t) => setActiveTableTab(t)}
        />
      )}

      {/* 5. Enhanced 3-View Data Table (Active Records, Skipped Duplicates, Saved CSV History) */}
      <DataTable
        records={records}
        duplicates={duplicates}
        historyFiles={historyFiles}
        activeTab={activeTableTab}
        setActiveTab={setActiveTableTab}
        entityType={parsedInfo?.entity_type || 'business'}
        selectedFields={selectedFields}
        defaultCsvFileName={outputCsvPath || (searchQuery.trim() && parsedInfo ? generateDefaultCsvFilename(parsedInfo) : '')}
        onViewRecord={(record) => setViewingRecord(record)}
        onEditRecord={(record) => setEditingRecord(record)}
        onDeleteRecord={handleDeleteRecord}
        onClearAll={handleClearAll}
        onExportCsv={handleExportCsv}
        onLoadHistoryCsv={handleLoadHistoryCsv}
        onDeleteHistoryCsv={handleDeleteHistoryCsv}
        onForceIncludeDuplicate={handleForceIncludeDuplicate}
        onClearDuplicates={handleClearDuplicates}
        onRefreshHistory={refreshHistoryFiles}
      />

      {/* View Record Details Modal */}
      <ViewRecordModal
        record={viewingRecord}
        isOpen={!!viewingRecord}
        onClose={() => setViewingRecord(null)}
        onEdit={(record) => {
          setViewingRecord(null);
          setEditingRecord(record);
        }}
      />

      {/* Edit Record Modal */}
      <EditRecordModal
        record={editingRecord}
        isOpen={!!editingRecord}
        onClose={() => setEditingRecord(null)}
        onSave={handleSaveEditedRecord}
      />

      {/* SweetAlert Delete Single Record Confirmation Modal */}
      <ConfirmDeleteModal
        isOpen={!!recordToDelete}
        record={recordToDelete}
        onConfirm={handleConfirmDelete}
        onCancel={() => setRecordToDelete(null)}
      />

      {/* SweetAlert Delete CSV File from Disk Confirmation Modal */}
      <ConfirmDeleteModal
        isOpen={!!fileToDelete}
        file={fileToDelete}
        onConfirm={handleConfirmDeleteHistoryCsv}
        onCancel={() => setFileToDelete(null)}
      />

      {/* SweetAlert Clear Dataset Table Confirmation Modal */}
      <ConfirmDeleteModal
        isOpen={clearTableConfirmOpen}
        isClearTable={true}
        onConfirm={handleConfirmClearAll}
        onCancel={() => setClearTableConfirmOpen(false)}
      />

      {/* Exit Confirmation Modal */}
      <ExitConfirmModal
        isOpen={exitConfirmOpen}
        unsavedCount={records.length}
        onDownloadAndExit={handleDownloadAndExit}
        onExitWithoutSaving={handleExitWithoutSaving}
        onCancel={() => setExitConfirmOpen(false)}
      />

      {/* Toast Notifications */}
      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
