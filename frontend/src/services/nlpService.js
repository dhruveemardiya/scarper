/**
 * Client-Side NLP Query Parser & Geo Resolver:
 * Provides identical NLP query parsing and pincode resolution in Browser / Network mode.
 */

export const CITY_DATABASE = {
  rajkot: {
    name: "Rajkot",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "360001",
    pincodes: ["360001", "360002", "360003", "360004", "360005", "360006", "360007", "360021", "360024"],
    areas: {
      "Yagnik Road": ["360001"],
      "Dharmendra Road": ["360001"],
      "Bhaktinagar": ["360002"],
      "Aji Industrial": ["360003"],
      "150 Feet Ring Road": ["360004", "360005"],
      "Mavdi": ["360004"],
      "Kalawad Road": ["360005"],
      "Kalavad Road": ["360005"],
      "University Road": ["360005"],
      "Nana Mava": ["360005"],
      "Junction Plot": ["360006"],
      "Raiya Road": ["360007"],
      "Race Course": ["360001"],
      "Metoda GIDC": ["360021"],
      "Shapar Veraval": ["360024"]
    }
  },
  ahmedabad: {
    name: "Ahmedabad",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "380001",
    pincodes: ["380001", "380005", "380006", "380007", "380008", "380009", "380013", "380014", "380015", "380051", "380052", "380054", "380058", "380059", "380060", "382330", "382350", "382424", "382481"],
    areas: {
      "Lal Darwaja": ["380001"],
      "Ellisbridge": ["380006"],
      "Paldi": ["380007"],
      "Maninagar": ["380008"],
      "Navrangpura": ["380009"],
      "C G Road": ["380009"],
      "Ashram Road": ["380009", "380014"],
      "Naranpura": ["380013"],
      "Satellite": ["380015"],
      "Satellite Road": ["380015"],
      "Vastrapur": ["380015"],
      "Prahlad Nagar": ["380015", "380051"],
      "Memnagar": ["380052"],
      "Gurukul": ["380052"],
      "Bodakdev": ["380054"],
      "SG Highway": ["380054", "380059"],
      "Sindhubhavan Road": ["380054", "380059"],
      "Bopal": ["380058"],
      "South Bopal": ["380058"],
      "Thaltej": ["380059"],
      "Science City": ["380060"],
      "Gota": ["382481"],
      "Chandkheda": ["382424"],
      "Motera": ["380005"],
      "Nikol": ["382350"],
      "Naroda": ["382330"]
    }
  },
  surat: {
    name: "Surat",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "395003",
    pincodes: ["395001", "395002", "395003", "395004", "395005", "395006", "395007", "395009"],
    areas: {
      "Ring Road": ["395002"],
      "Varachha": ["395006"],
      "Athwa Lines": ["395001"],
      "Adajan": ["395009"],
      "Piplod": ["395007"],
      "Vesu": ["395007"],
      "Rander": ["395005"],
      "Katargam": ["395004"]
    }
  },
  vadodara: {
    name: "Vadodara",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "390001",
    pincodes: ["390001", "390002", "390005", "390007", "390011", "390012", "390019", "390020"],
    areas: {
      "Alkapuri": ["390007"],
      "Sayajigunj": ["390005"],
      "Fatehgunj": ["390002"],
      "Manjalpur": ["390011"],
      "Gotri": ["390021"],
      "Karelibaug": ["390018"],
      "Vasna Road": ["390015"],
      "Akota": ["390020"]
    }
  },
  junagadh: {
    name: "Junagadh",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "362001",
    pincodes: ["362001", "362002", "362003", "362004", "362015", "362016", "362020"],
    areas: {
      "City Centre": ["362001"],
      "Zanzarda Road": ["362001", "362002"],
      "Joshipura": ["362002"],
      "Motibaug": ["362001", "362004"],
      "Bhavnath": ["362004"],
      "Timbavadi": ["362015"],
      "Dolatpara": ["362020"]
    }
  },
  jamnagar: {
    name: "Jamnagar",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "361001",
    pincodes: ["361001", "361002", "361003", "361004", "361005", "361006", "361007", "361008"],
    areas: {
      "City Centre": ["361001"],
      "Patel Colony": ["361008"],
      "Digjam Circle": ["361006"],
      "GIDC": ["361004", "361005"],
      "Gulabnagar": ["361007"]
    }
  },
  bhavnagar: {
    name: "Bhavnagar",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "364001",
    pincodes: ["364001", "364002", "364003", "364004", "364005", "364006"],
    areas: {
      "Waghawadi Road": ["364002"],
      "Kalanala": ["364001"],
      "Chitra GIDC": ["364004"],
      "Ghogha Road": ["364001"],
      "Subhashnagar": ["364005"]
    }
  },
  gandhinagar: {
    name: "Gandhinagar",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "382010",
    pincodes: ["382010", "382016", "382021", "382024", "382028", "382421", "382426", "382355"],
    areas: {
      "Sector 1 to 10": ["382010"],
      "Sector 11 to 20": ["382016", "382021"],
      "Sector 21 to 30": ["382024", "382028"],
      "Infocity": ["382421"],
      "Gift City": ["382355"]
    }
  },
  morbi: {
    name: "Morbi",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "363641",
    pincodes: ["363641", "363642", "363643", "363644"],
    areas: {
      "Sanala Road": ["363641"],
      "Lakhdhirpur Road": ["363642"],
      "Wankaner Road": ["363643"]
    }
  },
  anand: {
    name: "Anand",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "388001",
    pincodes: ["388001", "388120", "388121", "388315"],
    areas: {
      "Station Road": ["388001"],
      "Vallabh Vidyanagar": ["388120"],
      "GIDC": ["388121"]
    }
  },
  nadiad: {
    name: "Nadiad",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "387001",
    pincodes: ["387001", "387002", "387003"],
    areas: {
      "College Road": ["387001"],
      "GIDC": ["387003"]
    }
  },
  porbandar: {
    name: "Porbandar",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "360575",
    pincodes: ["360575", "360576", "360577", "360579"],
    areas: {
      "MG Road": ["360575"],
      "Kamala Baug": ["360577"]
    }
  },
  bhuj: {
    name: "Bhuj",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "370001",
    pincodes: ["370001", "370020", "370040"],
    areas: {
      "Station Road": ["370001"],
      "Madhapar": ["370020"]
    }
  },
  gandhidham: {
    name: "Gandhidham",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "370201",
    pincodes: ["370201", "370205", "370210"],
    areas: {
      "Adipur": ["370205"],
      "Kandla Port": ["370210"]
    }
  },
  bharuch: {
    name: "Bharuch",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "392001",
    pincodes: ["392001", "392002", "392011", "393002"],
    areas: {
      "Station Road": ["392001"],
      "Ankleshwar GIDC": ["393002"]
    }
  },
  navsari: {
    name: "Navsari",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "396445",
    pincodes: ["396445", "396446", "396447"],
    areas: {
      "Lunsikui": ["396445"],
      "GIDC": ["396447"]
    }
  },
  valsad: {
    name: "Valsad",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "396001",
    pincodes: ["396001", "396002", "396035"],
    areas: {
      "Tithal Road": ["396001"],
      "GIDC": ["396035"]
    }
  },
  vapi: {
    name: "Vapi",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "396191",
    pincodes: ["396191", "396195"],
    areas: {
      "GIDC": ["396195"],
      "Gunjan": ["396191"]
    }
  },
  mehsana: {
    name: "Mehsana",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "384001",
    pincodes: ["384001", "384002", "384003"],
    areas: {
      "Radhanpur Road": ["384002"],
      "GIDC": ["384002"]
    }
  },
  surendranagar: {
    name: "Surendranagar",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "363001",
    pincodes: ["363001", "363002", "363030"],
    areas: {
      "Main Bazar": ["363001"],
      "Wadhwan": ["363030"]
    }
  },
  amreli: {
    name: "Amreli",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "365601",
    pincodes: ["365601", "365602"],
    areas: {
      "Station Road": ["365601"],
      "GIDC": ["365602"]
    }
  },
  veraval: {
    name: "Veraval",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "362265",
    pincodes: ["362265", "362266", "362268", "362269"],
    areas: {
      "Somnath": ["362268"],
      "GIDC": ["362269"]
    }
  },
  pune: {
    name: "Pune",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "411001",
    pincodes: ["411001", "411004", "411005", "411014", "411028", "411038", "411045", "411057"],
    areas: {
      "Shivajinagar": ["411005"],
      "Kothrud": ["411038"],
      "Viman Nagar": ["411014"],
      "Hinjewadi": ["411057"],
      "Baner": ["411045"],
      "Hadapsar": ["411028"]
    }
  },
  hyderabad: {
    name: "Hyderabad",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "500001",
    pincodes: ["500001", "500003", "500032", "500033", "500034", "500072", "500081"],
    areas: {
      "Banjara Hills": ["500034"],
      "Jubilee Hills": ["500033"],
      "Hitec City": ["500081"],
      "Gachibowli": ["500032"],
      "Kukatpally": ["500072"]
    }
  },
  chennai: {
    name: "Chennai",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "600001",
    pincodes: ["600001", "600004", "600017", "600020", "600040", "600042", "600096"],
    areas: {
      "T Nagar": ["600017"],
      "Adyar": ["600020"],
      "Velachery": ["600042"],
      "Anna Nagar": ["600040"],
      "OMR": ["600096"]
    }
  },
  kolkata: {
    name: "Kolkata",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "700001",
    pincodes: ["700001", "700016", "700019", "700091", "700156"],
    areas: {
      "Salt Lake": ["700091"],
      "Park Street": ["700016"],
      "Ballygunge": ["700019"],
      "New Town": ["700156"]
    }
  },
  jaipur: {
    name: "Jaipur",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "302001",
    pincodes: ["302001", "302004", "302017", "302020", "302021"],
    areas: {
      "Malviya Nagar": ["302017"],
      "Vaishali Nagar": ["302021"],
      "Mansarovar": ["302020"],
      "C-Scheme": ["302001"]
    }
  },
  lucknow: {
    name: "Lucknow",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "226001",
    pincodes: ["226001", "226005", "226010", "226016", "226024"],
    areas: {
      "Gomti Nagar": ["226010"],
      "Hazratganj": ["226001"],
      "Aliganj": ["226024"],
      "Indira Nagar": ["226016"]
    }
  },
  chandigarh: {
    name: "Chandigarh",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "160017",
    pincodes: ["160017", "160022", "160035", "160055", "160101"],
    areas: {
      "Sector 17": ["160017"],
      "Sector 35": ["160035"],
      "IT Park": ["160101"],
      "Mohali": ["160055"]
    }
  },
  indore: {
    name: "Indore",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "452001",
    pincodes: ["452001", "452002", "452010", "452014"],
    areas: {
      "Vijay Nagar": ["452010"],
      "Palasia": ["452001"],
      "Rajwada": ["452002"]
    }
  },
  bhopal: {
    name: "Bhopal",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "462001",
    pincodes: ["462001", "462003", "462011", "462016", "462042"],
    areas: {
      "MP Nagar": ["462011"],
      "Arera Colony": ["462016"],
      "Kolar Road": ["462042"]
    }
  },
  mumbai: {
    name: "Mumbai",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "400001",
    pincodes: ["400001", "400050", "400053", "400076", "400070"],
    areas: {
      "Bandra": ["400050"],
      "Andheri": ["400053", "400058"],
      "Powai": ["400076"],
      "Kurla": ["400070"]
    }
  },
  delhi: {
    name: "Delhi",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "110001",
    pincodes: ["110001", "110016", "110024", "110070"],
    areas: {
      "Connaught Place": ["110001"],
      "Hauz Khas": ["110016"],
      "Lajpat Nagar": ["110024"],
      "Vasant Kunj": ["110070"]
    }
  },
  bengaluru: {
    name: "Bengaluru",
    country: "India",
    postal_label: "Pincode",
    default_pincode: "560001",
    pincodes: ["560001", "560034", "560038", "560066", "560100"],
    areas: {
      "Koramangala": ["560034"],
      "Indiranagar": ["560038"],
      "Whitefield": ["560066"],
      "Electronic City": ["560100"]
    }
  },
  london: {
    name: "London",
    country: "UK",
    postal_label: "Postcode",
    default_pincode: "SW1A 1AA",
    pincodes: ["SW1", "W1", "EC1", "WC1", "E1", "SE1", "NW1", "N1"],
    areas: {
      "Westminster": ["SW1A", "SW1P"],
      "Soho": ["W1D", "W1F"],
      "Camden": ["NW1"],
      "City of London": ["EC1", "EC2"]
    }
  },
  leicester: {
    name: "Leicester",
    country: "UK",
    postal_label: "Postcode",
    default_pincode: "LE1 1AA",
    pincodes: ["LE1", "LE2", "LE3", "LE4", "LE5", "LE18"],
    areas: {
      "City Centre": ["LE1"],
      "Oadby": ["LE2"],
      "Wigston": ["LE18"]
    }
  },
  sheffield: {
    name: "Sheffield",
    country: "UK",
    postal_label: "Postcode",
    default_pincode: "S1 2JA",
    pincodes: ["S1", "S2", "S3", "S10", "S11", "LE18"],
    areas: {
      "City Centre": ["S1"],
      "Broomhill": ["S10"],
      "Ecclesall": ["S11"]
    }
  }
};

const KNOWN_ENTITY_MAPPINGS = {
  coaching: ["coaching institute", "coaching", "tuition", "classes", "training institute"],
  school: ["school", "schools", "academy", "high school", "vidyalaya", "vidhyalay", "primary school"],
  college: ["college", "colleges", "university", "campus"],
  hospital: ["hospital", "hospitals", "clinic", "clinics", "doctor", "doctors", "healthcare", "dispensary", "nursing home", "medical center", "mediclinic"],
  restaurant: ["restaurant", "restaurants", "cafe", "cafes", "diner", "eatery", "food", "dining", "bistro", "dhaba", "bakery", "restro", "sweets", "pizzeria", "burger"],
  gas_station: ["gas station", "gas stations", "petrol pump", "petrol pumps", "fuel station", "fuel stations", "filling station", "ev charging"],
  hotel: ["hotel", "hotels", "resort", "resorts", "motel", "lodge", "guest house", "stay"],
  gym: ["gym", "gyms", "fitness center", "fitness club", "workout", "crossfit"],
  salon: ["salon", "salons", "beauty parlour", "spa", "barber", "hair studio"],
  pharmacy: ["pharmacy", "pharmacies", "chemist", "medical store", "drugstore"],
  real_estate: ["real estate", "property", "realtor", "builders", "brokers"]
};

const HOSPITAL_SPECIALITIES = [
  "Multi-Speciality", "Dental", "Eye", "Ophthalmology", "Heart", "Cardiology",
  "Orthopedic", "Pediatric", "Gynecology", "Neurology", "ENT", "Skin", "Dermatology", "General Hospital"
];

// Country-aware Postcode Validator
export function validatePostcode(postcode, country = "India") {
  if (!postcode || typeof postcode !== 'string') return false;
  const clean = postcode.trim();
  const cUpper = (country || "India").toUpperCase();

  if (cUpper === "INDIA") {
    return /^[1-9]\d{5}$/.test(clean);
  } else if (cUpper === "UK") {
    return /^[A-Z]{1,2}\d[A-Z\d]?(\s*\d?[A-Z]{0,2})?$/i.test(clean);
  } else if (cUpper === "USA" || cUpper === "US") {
    return /^\d{5}(-\d{4})?$/.test(clean);
  } else {
    return /^[A-Z0-9 -]{3,10}$/i.test(clean);
  }
}

// Clean, Deduplicate, Sort Postcodes
export function normalizePostcodes(postcodes = [], country = "India") {
  const validSet = new Set();
  for (const p of postcodes) {
    if (!p) continue;
    let cleaned = String(p).trim();
    if ((country || "").toUpperCase() === "UK") {
      cleaned = cleaned.toUpperCase();
    }
    if (validatePostcode(cleaned, country)) {
      validSet.add(cleaned);
    }
  }
  return Array.from(validSet).sort();
}

// Multi-Level Client Postcode Resolver
export function resolveClientPostcodes({ country = "India", city = "", area = "", query = "" }) {
  const cleanCountry = country ? country.trim() : "India";
  const cleanCity = city ? city.trim() : "";
  const cleanArea = area ? area.trim() : "";
  const postalLabel = cleanCountry.toUpperCase() === "UK" ? "Postcode" : "Pincode";

  // Level 1: Local Geo Database
  const cityKey = cleanCity.toLowerCase();
  const cityInfo = CITY_DATABASE[cityKey];

  if (cityInfo) {
    // Level 2: Area Mapping
    if (cleanArea && cityInfo.areas) {
      for (const [areaName, pins] of Object.entries(cityInfo.areas)) {
        if (areaName.toLowerCase().includes(cleanArea.toLowerCase()) || cleanArea.toLowerCase().includes(areaName.toLowerCase())) {
          const norm = normalizePostcodes(pins, cleanCountry);
          if (norm.length > 0) {
            return {
              postcodes: norm,
              postal_label: postalLabel,
              source: "AREA_MAPPING"
            };
          }
        }
      }
    }

    // City-wide mapping
    const allPins = new Set();
    if (cityInfo.pincodes) {
      cityInfo.pincodes.forEach((p) => allPins.add(p));
    }
    if (cityInfo.areas) {
      Object.values(cityInfo.areas).forEach((pins) => {
        pins.forEach((p) => allPins.add(p));
      });
    }
    const norm = normalizePostcodes(Array.from(allPins), cleanCountry);
    if (norm.length > 0) {
      return {
        postcodes: norm,
        postal_label: postalLabel,
        source: "LOCAL_DATASET"
      };
    }
  }

  // Level 4: Query Address PIN extraction
  if (query) {
    const rawPins = [];
    if (cleanCountry.toUpperCase() === "INDIA") {
      const matches = query.match(/\b([1-9]\d{5})\b/g);
      if (matches) rawPins.push(...matches);
    } else if (cleanCountry.toUpperCase() === "UK") {
      const matches = query.match(/\b([A-Z]{1,2}\d[A-Z\d]?\s*\d?[A-Z]{0,2})\b/gi);
      if (matches) rawPins.push(...matches.map((m) => m.toUpperCase()));
    }
    const norm = normalizePostcodes(rawPins, cleanCountry);
    if (norm.length > 0) {
      return {
        postcodes: norm,
        postal_label: postalLabel,
        source: "ADDRESS_EXTRACTION"
      };
    }
  }

  return {
    postcodes: [],
    postal_label: postalLabel,
    source: "FALLBACK"
  };
}

export function parseSearchQuery(query) {
  return parseClientQuery(query);
}

export function parseClientQuery(query) {
  if (!query) return null;
  const cleaned = query.trim();
  const qLower = cleaned.toLowerCase();

  // 1. Detect Country
  let country = "India";
  if (/\b(uk|u\.k\.|united kingdom|england|britain|great britain|london|leicester|sheffield|birmingham|manchester)\b/i.test(qLower)) {
    country = "UK";
  }

  // 2. Detect Direct Pincode
  let detectedPincode = "";
  const pinMatch = cleaned.match(/\b([1-9]\d{5})\b/);
  if (pinMatch) {
    detectedPincode = pinMatch[1];
  } else if (country === "UK") {
    const ukMatch = cleaned.match(/\b([A-Z]{1,2}\d[A-Z\d]?\s*\d?[A-Z]{0,2})\b/i);
    if (ukMatch) detectedPincode = ukMatch[1].toUpperCase();
  }

  // 3. Detect City & Area
  let detectedCity = "";
  let detectedArea = "";

  for (const [cityKey, cityData] of Object.entries(CITY_DATABASE)) {
    const cityName = cityData.name;
    const reCity = new RegExp(`\\b(${cityKey}|${cityName})\\b`, "i");
    if (reCity.test(qLower)) {
      detectedCity = cityName;
      country = cityData.country || country;
      for (const area of Object.keys(cityData.areas || {})) {
        if (new RegExp(`\\b${area}\\b`, "i").test(qLower)) {
          detectedArea = area;
          break;
        }
      }
      break;
    }
  }

  // Dynamic location fallback from prepositions (e.g. 'school in Junagadh', 'hotel in Keshod')
  if (!detectedCity) {
    const locMatch = cleaned.match(/\b(?:in|near|at|around)\s+([a-zA-Z\s]+)/i);
    if (locMatch) {
      let cand = locMatch[1].trim();
      cand = cand.replace(/\b(india|uk|united kingdom|usa|gujarat|maharashtra|rajasthan)\b/gi, "").trim();
      if (cand && cand.length >= 3 && !["the", "all", "best", "top", "good", "city"].includes(cand.toLowerCase())) {
        detectedCity = cand.replace(/\b\w/g, (c) => c.toUpperCase());
        const cityKey = cand.toLowerCase();
        if (CITY_DATABASE[cityKey]) {
          detectedCity = CITY_DATABASE[cityKey].name;
          country = CITY_DATABASE[cityKey].country || country;
        }
      }
    }
  }

  // 4. Detect Entity Type & Label Dynamically
  let detectedEntity = "";
  let entityLabel = "";

  for (const [ent, triggers] of Object.entries(KNOWN_ENTITY_MAPPINGS)) {
    if (triggers.some((t) => new RegExp(`\\b${t}\\b`, "i").test(qLower))) {
      detectedEntity = ent;
      entityLabel = ent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      break;
    }
  }

  // Detect Speciality
  let detectedSpeciality = "";
  for (const spec of HOSPITAL_SPECIALITIES) {
    if (new RegExp(`\\b${spec}\\b`, "i").test(qLower)) {
      detectedSpeciality = spec;
      if (!detectedEntity || detectedEntity === "business") {
        detectedEntity = "hospital";
        entityLabel = qLower.includes("clinic") ? `${spec} Clinic` : `${spec} Hospital`;
      }
      break;
    }
  }

  // If still unknown, extract entity dynamically
  if (!detectedEntity) {
    let entityRaw = cleaned;
    const locationPatterns = [
      /\b(in|of|at|near|around|beside|across)\s+.*$/i,
      /\b(ahmedabad|rajkot|surat|vadodara|mumbai|delhi|bangalore|london|leicester|sheffield|birmingham|manchester|uk|india|gujarat)\b/gi,
      /\b\d{6}\b/g
    ];
    for (const pat of locationPatterns) {
      entityRaw = entityRaw.replace(pat, "");
    }
    entityRaw = entityRaw.replace(/^[ ,.\-/]+|[ ,.\-/]+$/g, "").trim();

    if (entityRaw) {
      entityLabel = entityRaw.replace(/\b\w/g, (c) => c.toUpperCase());
      detectedEntity = entityRaw.toLowerCase().replace(/[^a-z0-9]+/g, "_");
    } else {
      detectedEntity = "business";
      entityLabel = "Business";
    }
  }

  if (!entityLabel) {
    entityLabel = detectedEntity.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  // 5. Resolve Pincodes using Multi-Level Resolver
  const resolution = resolveClientPostcodes({
    country,
    city: detectedCity,
    area: detectedArea,
    query: cleaned
  });

  let resolvedPincodes = resolution.postcodes || [];
  const postalLabel = resolution.postal_label || (country === "UK" ? "Postcode" : "Pincode");

  if (detectedPincode && !resolvedPincodes.includes(detectedPincode)) {
    resolvedPincodes = [detectedPincode, ...resolvedPincodes];
  }

  return {
    raw_query: cleaned,
    entity_type: detectedEntity,
    entity_label: entityLabel,
    country,
    postal_label: postalLabel,
    city: detectedCity,
    area: detectedArea,
    pincode: detectedPincode,
    category: "",
    speciality: detectedSpeciality,
    food_type: "all",
    keyword: "",
    resolved_pincodes: resolvedPincodes,
    postcode_source: resolution.source
  };
}
