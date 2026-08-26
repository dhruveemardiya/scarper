"""
Geographical data module providing cities, areas, and automatic postal code (pincode/postcode) resolutions.
Supports multi-country resolution (India, UK, etc.).
"""

from typing import Dict, List, Optional, Any

# Multi-Country City -> Areas and their typical Pincodes/Postcodes
CITY_DATABASE: Dict[str, Dict[str, Any]] = {
    # ------------------ INDIA ------------------
    "rajkot": {
        "name": "Rajkot",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "360001",
        "areas": {
            "Yagnik Road": ["360001"],
            "Dharmendra Road": ["360001"],
            "Kotecha Chowk": ["360001"],
            "Bhaktinagar": ["360002"],
            "Dhebar Road": ["360002"],
            "Aji Industrial": ["360003"],
            "Kothariya": ["360003", "360022"],
            "150 Feet Ring Road": ["360004", "360005"],
            "Gondal Road": ["360004"],
            "Mavdi": ["360004"],
            "Kalawad Road": ["360005"],
            "Kalavad Road": ["360005"],
            "University Road": ["360005"],
            "Nana Mava": ["360005"],
            "Junction Plot": ["360006"],
            "Madhapar": ["360006"],
            "Raiya Road": ["360007"],
            "Race Course": ["360001"],
            "Pedak Road": ["360003"],
            "Sant Kabir Road": ["360003"],
            "Metoda GIDC": ["360021"],
            "Shapar Veraval": ["360024"]
        }
    },
    "ahmedabad": {
        "name": "Ahmedabad",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "380001",
        "areas": {
            "Lal Darwaja / Relief Rd": ["380001"],
            "Ellisbridge": ["380006"],
            "Paldi": ["380007"],
            "Maninagar": ["380008"],
            "Navrangpura": ["380009"],
            "C G Road": ["380009"],
            "Ashram Road": ["380009", "380014"],
            "Naranpura": ["380013"],
            "Satellite": ["380015"],
            "Vastrapur": ["380015"],
            "Prahlad Nagar": ["380015", "380051"],
            "Ambawadi": ["380015", "380006"],
            "Memnagar": ["380052"],
            "Gurukul": ["380052"],
            "Bodakdev": ["380054"],
            "SG Highway": ["380054", "380059", "380060"],
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
    "surat": {
        "name": "Surat",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "395003",
        "areas": {
            "Ring Road": ["395002"],
            "Varachha": ["395006"],
            "Athwa Lines": ["395001"],
            "Adajan": ["395009"],
            "Piplod": ["395007"],
            "Vesu": ["395007"],
            "Rander": ["395005"],
            "Katargam": ["395004"],
            "Ghod Dod Road": ["395007"]
        }
    },
    "vadodara": {
        "name": "Vadodara",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "390001",
        "areas": {
            "Alkapuri": ["390007"],
            "Sayajigunj": ["390005"],
            "Fatehgunj": ["390002"],
            "Gotri": ["390021"],
            "Manjalpur": ["390011"],
            "Akota": ["390020"],
            "Vasna Road": ["390015"],
            "Karelibaug": ["390018"]
        }
    },
    "junagadh": {
        "name": "Junagadh",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "362001",
        "areas": {
            "City Centre / MG Road": ["362001"],
            "Zanzarda Road": ["362001", "362002"],
            "Joshipura": ["362002"],
            "Motibaug / Agriculture": ["362001", "362004"],
            "Bhavnath": ["362004"],
            "Timbavadi": ["362015"],
            "Dolatpara GIDC": ["362020"]
        }
    },
    "jamnagar": {
        "name": "Jamnagar",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "361001",
        "areas": {
            "City Centre / Bedi Gate": ["361001"],
            "Patel Colony": ["361008"],
            "Digjam Circle": ["361006"],
            "GIDC Phase 1 / 2": ["361004", "361005"],
            "Khodiyar Colony": ["361006"],
            "Gulabnagar": ["361007"],
            "Bedi Port": ["361009"]
        }
    },
    "bhavnagar": {
        "name": "Bhavnagar",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "364001",
        "areas": {
            "Waghawadi Road": ["364002"],
            "Kalanala": ["364001"],
            "Chitra GIDC": ["364004"],
            "Ghogha Road": ["364001"],
            "Takhteshwar": ["364002"],
            "Subhashnagar": ["364005"],
            "Kumbharwada": ["364006"]
        }
    },
    "gandhinagar": {
        "name": "Gandhinagar",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "382010",
        "areas": {
            "Sector 1 to 10": ["382010"],
            "Sector 11 to 20": ["382016", "382021"],
            "Sector 21 to 30": ["382024", "382028"],
            "Infocity / Kudasan": ["382421"],
            "Sargasan": ["382421"],
            "Randesan / Raysan": ["382426"],
            "Gift City": ["382355"]
        }
    },
    "morbi": {
        "name": "Morbi",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "363641",
        "areas": {
            "Sanala Road": ["363641"],
            "Kandla Highway": ["363642"],
            "Lakhdhirpur Road GIDC": ["363642"],
            "Trajpar": ["363641"],
            "Wankaner Road": ["363643"]
        }
    },
    "anand": {
        "name": "Anand",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "388001",
        "areas": {
            "Station Road": ["388001"],
            "Vallabh Vidyanagar": ["388120"],
            "Bakrol": ["388315"],
            "GIDC Anand": ["388121"],
            "Amul Dairy Road": ["388001"]
        }
    },
    "nadiad": {
        "name": "Nadiad",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "387001",
        "areas": {
            "College Road": ["387001"],
            "Petlad Road": ["387002"],
            "GIDC Nadiad": ["387003"],
            "Santram Road": ["387001"]
        }
    },
    "porbandar": {
        "name": "Porbandar",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "360575",
        "areas": {
            "MG Road": ["360575"],
            "Chowpati": ["360575"],
            "Kamala Baug": ["360577"],
            "GIDC Porbandar": ["360579"]
        }
    },
    "bhuj": {
        "name": "Bhuj",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "370001",
        "areas": {
            "Station Road": ["370001"],
            "Madhapar": ["370020"],
            "Mirzapar": ["370040"],
            "Mundra Road": ["370001"]
        }
    },
    "gandhidham": {
        "name": "Gandhidham",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "370201",
        "areas": {
            "Sector 1 to 5": ["370201"],
            "Sector 6 to 10": ["370201"],
            "Adipur": ["370205"],
            "Kandla Port": ["370210"]
        }
    },
    "bharuch": {
        "name": "Bharuch",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "392001",
        "areas": {
            "Station Road": ["392001"],
            "Zadeshwar Road": ["392011"],
            "Bholav": ["392002"],
            "Ankleshwar GIDC": ["393002"]
        }
    },
    "navsari": {
        "name": "Navsari",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "396445",
        "areas": {
            "Lunsikui": ["396445"],
            "Fuwara": ["396445"],
            "Jalalpor": ["396446"],
            "GIDC Navsari": ["396447"]
        }
    },
    "valsad": {
        "name": "Valsad",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "396001",
        "areas": {
            "Tithal Road": ["396001"],
            "Dharampur Road": ["396002"],
            "Gundlav GIDC": ["396035"]
        }
    },
    "vapi": {
        "name": "Vapi",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "396191",
        "areas": {
            "GIDC Vapi": ["396195"],
            "Gunjan": ["396191"],
            "Chala": ["396191"],
            "Daman Road": ["396191"]
        }
    },
    "mehsana": {
        "name": "Mehsana",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "384001",
        "areas": {
            "Radhanpur Road": ["384002"],
            "Modhera Road": ["384002"],
            "GIDC Mehsana": ["384002"],
            "City Area": ["384001"]
        }
    },
    "surendranagar": {
        "name": "Surendranagar",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "363001",
        "areas": {
            "Main Bazar": ["363001"],
            "Wadhwan": ["363030"],
            "Dhrangadhra": ["363310"],
            "GIDC Surendranagar": ["363002"]
        }
    },
    "amreli": {
        "name": "Amreli",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "365601",
        "areas": {
            "Station Road": ["365601"],
            "Chakkargadh Road": ["365601"],
            "GIDC Amreli": ["365602"]
        }
    },
    "veraval": {
        "name": "Veraval",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Gujarat",
        "default_pincode": "362265",
        "areas": {
            "Somnath Temple Area": ["362268"],
            "Rayon Factory Area": ["362266"],
            "GIDC Veraval": ["362269"]
        }
    },
    "pune": {
        "name": "Pune",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Maharashtra",
        "default_pincode": "411001",
        "areas": {
            "Shivajinagar": ["411005"],
            "Kothrud": ["411038"],
            "Viman Nagar": ["411014"],
            "Hinjewadi": ["411057"],
            "Baner": ["411045"],
            "Wakad": ["411057"],
            "Hadapsar / Magarpatta": ["411028"],
            "Kalyani Nagar": ["411006"],
            "Aundh": ["411007"]
        }
    },
    "hyderabad": {
        "name": "Hyderabad",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Telangana",
        "default_pincode": "500001",
        "areas": {
            "Banjara Hills": ["500034"],
            "Jubilee Hills": ["500033"],
            "Hitec City": ["500081"],
            "Gachibowli": ["500032"],
            "Madhapur": ["500081"],
            "Kukatpally": ["500072"],
            "Secunderabad": ["500003"]
        }
    },
    "chennai": {
        "name": "Chennai",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Tamil Nadu",
        "default_pincode": "600001",
        "areas": {
            "T Nagar": ["600017"],
            "Adyar": ["600020"],
            "Velachery": ["600042"],
            "Anna Nagar": ["600040"],
            "OMR / IT Corridor": ["600096", "600097"],
            "Mylapore": ["600004"]
        }
    },
    "kolkata": {
        "name": "Kolkata",
        "country": "India",
        "postal_label": "Pincode",
        "state": "West Bengal",
        "default_pincode": "700001",
        "areas": {
            "Salt Lake / Sector V": ["700091"],
            "Park Street": ["700016"],
            "Ballygunge": ["700019"],
            "New Town": ["700156"],
            "Howrah": ["711101"]
        }
    },
    "jaipur": {
        "name": "Jaipur",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Rajasthan",
        "default_pincode": "302001",
        "areas": {
            "Malviya Nagar": ["302017"],
            "Vaishali Nagar": ["302021"],
            "Mansarovar": ["302020"],
            "C-Scheme": ["302001"],
            "Raja Park": ["302004"]
        }
    },
    "lucknow": {
        "name": "Lucknow",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Uttar Pradesh",
        "default_pincode": "226001",
        "areas": {
            "Gomti Nagar": ["226010"],
            "Hazratganj": ["226001"],
            "Aliganj": ["226024"],
            "Indira Nagar": ["226016"],
            "Alambagh": ["226005"]
        }
    },
    "chandigarh": {
        "name": "Chandigarh",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Chandigarh",
        "default_pincode": "160017",
        "areas": {
            "Sector 17": ["160017"],
            "Sector 35": ["160035"],
            "Sector 22": ["160022"],
            "IT Park": ["160101"],
            "Mohali": ["160055"],
            "Panchkula": ["134109"]
        }
    },
    "indore": {
        "name": "Indore",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Madhya Pradesh",
        "default_pincode": "452001",
        "areas": {
            "Vijay Nagar": ["452010"],
            "Palasia": ["452001"],
            "Rajwada": ["452002"],
            "Bhawarkua": ["452014"],
            "AB Road": ["452010"]
        }
    },
    "bhopal": {
        "name": "Bhopal",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Madhya Pradesh",
        "default_pincode": "462001",
        "areas": {
            "MP Nagar": ["462011"],
            "Arera Colony": ["462016"],
            "Kolar Road": ["462042"],
            "New Market": ["462003"]
        }
    },
    "mumbai": {
        "name": "Mumbai",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Maharashtra",
        "default_pincode": "400001",
        "areas": {
            "Fort / Colaba": ["400001", "400005"],
            "Bandra West": ["400050"],
            "Andheri West": ["400053"],
            "Andheri East": ["400069"],
            "Juhu": ["400049"],
            "Powai": ["400076"],
            "Goregaon West": ["400062"],
            "Borivali West": ["400092"],
            "Dadar West": ["400028"],
            "Lower Parel": ["400013"]
        }
    },
    "delhi": {
        "name": "Delhi",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Delhi",
        "default_pincode": "110001",
        "areas": {
            "Connaught Place": ["110001"],
            "Hauz Khas": ["110016"],
            "Saket": ["110017"],
            "Lajpat Nagar": ["110024"],
            "Karol Bagh": ["110005"],
            "Dwarka": ["110075"],
            "Rohini": ["110085"],
            "Vasant Kunj": ["110070"]
        }
    },
    "bengaluru": {
        "name": "Bengaluru",
        "country": "India",
        "postal_label": "Pincode",
        "state": "Karnataka",
        "default_pincode": "560001",
        "areas": {
            "Indiranagar": ["560038"],
            "Koramangala": ["560034"],
            "Whitefield": ["560066"],
            "HSR Layout": ["560102"],
            "Jayanagar": ["560041"],
            "MG Road": ["560001"],
            "Electronic City": ["560100"]
        }
    },

    # ------------------ UK ------------------
    "london": {
        "name": "London",
        "country": "UK",
        "postal_label": "Postcode",
        "state": "Greater London",
        "default_pincode": "EC1A 1BB",
        "areas": {
            "City of London": ["EC1A", "EC2A", "EC3A", "EC4A"],
            "Westminster / Soho": ["W1D", "W1F", "WC2H", "SW1A"],
            "Camden": ["NW1", "NW5"],
            "Islington": ["N1"],
            "Kensington & Chelsea": ["SW3", "SW7", "W8"],
            "Hackney / Shoreditch": ["E1", "E2", "EC2A"],
            "Southwark / London Bridge": ["SE1"],
            "Greenwich": ["SE10"]
        }
    },
    "leicester": {
        "name": "Leicester",
        "country": "UK",
        "postal_label": "Postcode",
        "state": "Leicestershire",
        "default_pincode": "LE1 1AA",
        "areas": {
            "City Centre": ["LE1"],
            "Clarendon Park / Highfields": ["LE2"],
            "Braunstone / West End": ["LE3"],
            "Belgrave / Rushey Mead": ["LE4"],
            "Evington / Hamilton": ["LE5"],
            "Fosse Park / Enderby": ["LE19"],
            "Oadby / Wigston": ["LE2"]
        }
    },
    "sheffield": {
        "name": "Sheffield",
        "country": "UK",
        "postal_label": "Postcode",
        "state": "South Yorkshire",
        "default_pincode": "S1 2AA",
        "areas": {
            "City Centre": ["S1"],
            "Highfield / Arbourthorne": ["S2"],
            "Broomhall / Neepsend": ["S3"],
            "Ranmoor / Crookes": ["S10"],
            "Ecclesall / Sharrow": ["S11"]
        }
    },
    "birmingham": {
        "name": "Birmingham",
        "country": "UK",
        "postal_label": "Postcode",
        "state": "West Midlands",
        "default_pincode": "B1 1AA",
        "areas": {
            "City Centre": ["B1", "B2", "B3", "B5"],
            "Jewellery Quarter": ["B18"],
            "Edgbaston": ["B15"],
            "Moseley / Kings Heath": ["B13", "B14"],
            "Selly Oak": ["B29"]
        }
    },
    "manchester": {
        "name": "Manchester",
        "country": "UK",
        "postal_label": "Postcode",
        "state": "Greater Manchester",
        "default_pincode": "M1 1AA",
        "areas": {
            "City Centre": ["M1", "M2", "M3", "M4"],
            "Northern Quarter": ["M4"],
            "Ancoats": ["M4"],
            "Didsbury": ["M20"],
            "Chorlton": ["M21"],
            "Fallowfield": ["M14"]
        }
    }
}

def normalize_city_key(city_str: str) -> str:
    if not city_str:
        return ""
    key = city_str.strip().lower()
    aliases = {
        "bangalore": "bengaluru",
        "baroda": "vadodara",
        "bombay": "mumbai",
        "new delhi": "delhi",
        "amdavad": "ahmedabad"
    }
    return aliases.get(key, key)

def get_city_info(city_name: str) -> Optional[Dict[str, Any]]:
    key = normalize_city_key(city_name)
    return CITY_DATABASE.get(key)

def get_areas_for_city(city_name: str) -> List[str]:
    info = get_city_info(city_name)
    if info and "areas" in info:
        return list(info["areas"].keys())
    return []

def get_pincodes_for_city_area(city_name: str, area_name: Optional[str] = None) -> List[str]:
    info = get_city_info(city_name)
    if not info:
        return []
    
    if area_name and area_name.lower() not in ["all", "all areas", ""]:
        for area, pins in info["areas"].items():
            if area.lower() == area_name.lower() or area_name.lower() in area.lower():
                return pins
                
    # If no area specified, collect all unique pincodes/postcodes for that city
    all_pins = set()
    for pins in info["areas"].values():
        all_pins.update(pins)
    return sorted(list(all_pins))

def find_city_by_area_or_pincode(query_token: str) -> Optional[Dict[str, str]]:
    """Tries to find city and area if token matches a known area or postal code."""
    token = query_token.strip().lower()
    if not token or len(token) < 3 or token in ["the", "and", "for", "near", "best", "all", "top"]:
        return None

    for city_key, city_data in CITY_DATABASE.items():
        for area, pins in city_data["areas"].items():
            area_lower = area.lower()
            if token in [p.lower() for p in pins]:
                return {
                    "city": city_data["name"],
                    "country": city_data.get("country", "India"),
                    "area": area,
                    "pincode": token
                }
            if token == area_lower or (len(token) >= 4 and token in area_lower.split()):
                return {
                    "city": city_data["name"],
                    "country": city_data.get("country", "India"),
                    "area": area,
                    "pincode": pins[0] if pins else ""
                }
    return None
