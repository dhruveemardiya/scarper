# DataScraper Desktop - Local Business Intelligence Application

A high-performance Windows desktop application built with **React**, **Electron**, and **Python (Selenium + BeautifulSoup4 + Pandas)** designed for searching, scraping, and exporting structured business data for **Restaurants**, **Hospitals**, and extensible business categories without any database or backend server dependencies.

---

## 🌟 Key Features

1. **Zero Database / Pure In-Memory Architecture**:
   - Holds scraped and manually created records in-memory during active sessions.
   - Prominent data-loss warning banner and exit confirmation dialog to protect against accidental exits.
2. **Intelligent Natural Language Query Parser**:
   - Parses queries such as `restaurants of Ahmedabad`, `hospitals of Rajkot`, `veg restaurants in Satellite Ahmedabad`, `dental hospitals in Rajkot`, `restaurants near 380015`.
   - Extracts entity type, city, area, pincode, food type, and speciality.
3. **Dynamic Multi-Level Suggestions**:
   - Generates category suggestions (*Veg, Non-Veg, Cafes, Fast Food, Family Restaurants, Fine Dining, Multi-Cuisine, Multi-Speciality, Dental Clinics, Eye Hospitals, Heart Hospitals*).
   - Generates city-specific area suggestions (*Satellite, SG Highway, Navrangpura, Bopal, Kalawad Road, University Road, etc.*).
   - Dynamic pincode autocomplete and auto-resolution (*e.g., Satellite → 380015*).
4. **Resilient Public Scraping Engine (Selenium + BS4)**:
   - Headless Chrome/Edge WebDriver with anti-detection flags.
   - BeautifulSoup4 HTML parser extracting Name, Category, Veg/Non-Veg, Address, Area, City, Pincode, Phone Number, Rating, Reviews, Timings, Doctors, Coordinates, and Source URLs.
   - Record-by-record progressive streaming straight into the React UI.
5. **In-Memory Duplicate Detection**:
   - Normalized composite hashing across business names, phone numbers, and addresses.
6. **Direct CSV Export (Pandas + Electron Save Dialog)**:
   - Native Windows Save File dialog.
   - Exports structured CSV matching standard schemas plus user custom columns.
7. **Manual Controls & Custom Search**:
   - `+ Custom Search`: override any combination of parameters.
   - `+ Add Record`: manually enter records.
   - Inline/modal record editing before export.

---

## 🌐 Unified Local & LAN Network Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   HOST MACHINE (PC)                    │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │       Python Scraper Engine & Network Bridge     │  │
│  │               Listening on 0.0.0.0:8765          │  │
│  │                                                  │  │
│  │   • HTTP API (/api/state, /api/parse, etc.)      │  │
│  │   • WebSocket Hub (Live streaming to all clients)│  │
│  │   • Authoritative State Manager                  │  │
│  │   • Selenium Chrome + BeautifulSoup Parser       │  │
│  │   • Immediate CSV Disk Appender                  │  │
│  └──────────────────────────┬───────────────────────┘  │
│                             │                           │
│              HTTP & WebSocket Connection                │
│                             │                           │
│         ┌───────────────────┴───────────────────┐       │
│         ▼                                       ▼       │
│  ┌──────────────┐                       ┌──────────────┐│
│  │  Electron /  │                       │  Local Web   ││
│  │ Desktop App  │                       │localhost:5173││
│  └──────────────┘                       └──────────────┘│
└────────────────────────────────────────────────────────┘
                              ▲
                 Wi-Fi / LAN Network Connection
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       ┌────────────────┐           ┌────────────────┐
       │ Remote Laptop  │           │ Mobile/Tablet  │
       │192.168.x.x:5173│           │192.168.x.x:5173│
       └────────────────┘           └────────────────┘
```

### Access URLs:
* **Local Machine**: `http://localhost:5173`
* **LAN / Wi-Fi Network Devices**: `http://<PC_LAN_IP>:5173` (e.g. `http://192.168.1.13:5173`)
* **Scraper Network Bridge**: `http://<PC_LAN_IP>:8765` / `ws://<PC_LAN_IP>:8765/ws`

---

## 🏗️ Architecture

```text
React UI (Vite + Desktop Theme)
       │
       ▼  (Safe contextBridge IPC)
Electron Main Process (`python_bridge.js`)
       │
       ▼  (JSON stdio streaming)
Local Python Process (`run_scraper.py`)
       │
       ▼
Selenium WebDriver (Headless Chrome / Edge) + BeautifulSoup4
       │
       ▼
In-Memory Dataset & Live Event Stream
       │
       ▼
React Live Data Table & Real-time Progress HUD
       │
       ▼
Direct CSV Export (Electron Save Dialog / Pandas)
```

---

## 🚀 Running the Application

### 1. Prerequisites
- **Node.js**: v18+ (tested on Node v24)
- **Python**: 3.10+ (tested on Python 3.12)
- **Google Chrome** or **Microsoft Edge** installed on Windows

### 2. Python Dependencies
```bash
pip install -r python/requirements.txt
```

### 3. Frontend & Electron Dependencies
```bash
npm install
cd frontend && npm install && cd ..
```

### 4. Start Development Mode
To launch the React dev server with hot reload and Electron window:
```bash
npm run dev
```

---

## 🧪 Running Automated Tests

Run the Python verification test suite:
```bash
python python/test_scraper_suite.py
```
