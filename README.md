# GTM Intelligence Dashboard

A comprehensive Go-To-Market analytics dashboard built as a single HTML file. Tracks 100 metrics across 7 business domains with interactive filters, 21 chart types, and real-time data re-aggregation from 50K synthetic deal records.

![Dashboard](https://img.shields.io/badge/Charts-21%20Types-D97757) ![Metrics](https://img.shields.io/badge/Metrics-100-4E8A6E) ![Filters](https://img.shields.io/badge/Filters-7-5B7FBA)

---

## What It Does

Simulates a full GTM ops dashboard that a revenue team would use. Every filter change re-computes all KPIs and charts from the underlying deal-level data — no static screenshots, no mock numbers.

**7 Tabs:**

| Tab | Metrics | Focus |
|-----|---------|-------|
| Pipeline | 20 | Deal flow, stage conversion, velocity, win/loss analysis |
| Revenue | 20 | ARR/MRR trends, bookings, retention (NRR/GRR), quota attainment |
| Customer | 15 | Churn, CLV, CAC payback, LTV:CAC, segment breakdown |
| Contacts & Leads | 15 | MQL/SQL volume, funnel conversion, lead scoring, data quality |
| Marketing | 10 | Attribution (first/last touch), channel mix, cost per lead/MQL/opp |
| Finance | 10 | Invoicing, DSO, collections, discounts, refunds |
| Activity | 10 | Rep productivity, meetings, CRM hygiene, engagement scoring |

## Chart Types Used

The dashboard uses **21 distinct visualization types** mapped to the most semantically appropriate metric:

- **Standard**: Bar, Horizontal Bar, Grouped Bar, Stacked Bar
- **Trends**: Line, Area, Stacked Area, Step Line, Spline
- **Distribution**: Pie, Donut, Polar Area, Histogram
- **Comparison**: Radar, Scatter, Bubble
- **KPI**: Gauge, Combo (bar + line overlay), Waterfall
- **Spatial**: Leaflet.js geographic bubble map (CartoDB Voyager tiles)
- **Matrix**: Color-coded performance heatmap

## Filters

7 interactive filters that re-aggregate all data on change:

- **Year** — 2022, 2023, 2024
- **Segment** — SMB, Mid-Market, Enterprise
- **Region** — India (South/North/West/East), SEA, Middle East, ANZ, UK, Europe, North America
- **Industry** — SaaS, FinTech, HealthTech, E-commerce, Enterprise IT, EdTech, Logistics, Manufacturing, Retail, BFSI
- **Rep** — 20 sales reps
- **Source** — Outbound SDR, Inbound Demo, Partner Referral, Events, Paid Search, Organic SEO, Customer Referral, LinkedIn
- **Stage** — Prospect through Closed Won/Lost

## How It Works

### Data Pipeline

```
generate_data.py          build_dashboard.py         gtm_dashboard_final.html
─────────────────         ──────────────────         ────────────────────────
Faker + NumPy             Reads CSVs                 Single self-contained
generates 5 CSVs:         Aggregates into            HTML file with:
- contacts (300K)         pre-computed JSON           - Embedded JSON data
- deals (50K)             with monthly series,        - 50K deal records
- customers (12K)         group breakdowns,           - Tab-based rendering
- invoices (45K)          stage counts, KPIs          - Filter → re-aggregate
- orders (30K)                                        - Leaflet.js map
```

### Client-Side Deal Engine

On page load, a seeded PRNG generates ~50K compact deal records `[monthIdx, segIdx, regIdx, indIdx, repIdx, srcIdx, stgIdx, amount, cycleDays]` matching the original data distributions. When any filter changes:

1. Deals are filtered by selected criteria
2. `computeD()` re-aggregates filtered deals into the full metrics structure
3. KPI cards update
4. Active tab's charts re-render

### Memory Management

- Only the active tab's charts exist in memory (~12-18 Chart.js instances)
- All charts are destroyed on tab switch before rendering new ones
- Leaflet map instance is properly cleaned up on navigation
- Deal records use compact 9-element arrays (~2MB total)

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [Chart.js](https://www.chartjs.org/) | 4.4.1 | 19 chart types (bar, line, radar, polar, scatter, bubble, etc.) |
| [Leaflet](https://leafletjs.com/) | 1.9.4 | Interactive geographic map with real tile layers |
| [CartoDB Voyager](https://carto.com/basemaps/) | — | Warm-toned map tiles |
| [DM Sans](https://fonts.google.com/specimen/DM+Sans) | — | UI typography |
| [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) | — | Numeric/data typography |

No build tools. No bundler. No framework. One HTML file.

## Project Structure

```
revenue-dashboard/
├── gtm_dashboard_final.html   # The dashboard (self-contained)
├── generate_data.py           # Synthetic data generator (Faker + Pandas)
├── build_dashboard.py         # Aggregates CSVs → dashboard JSON
├── terms.json                 # 100 metric definitions, benchmarks, formulas
├── charts.txt                 # Reference list of chart types
├── data/
│   ├── contacts.csv           # 300K contact records
│   ├── deals.csv              # 50K deal records
│   ├── customers.csv          # 12K customer records
│   ├── invoices.csv           # 45K invoice records
│   └── orders.csv             # 30K order records
└── README.md
```

## Quick Start

**Just open the dashboard:**
```
open gtm_dashboard_final.html
```
No server needed. Works in any modern browser.

**To regenerate data from scratch:**
```bash
pip install faker pandas numpy
python generate_data.py        # Creates CSVs in data/
python build_dashboard.py      # Builds the dashboard HTML
```

## Design

Built with a warm, cream-toned theme inspired by Claude's aesthetic:

- **Background**: `#FAF6F0` warm parchment
- **Cards**: `#FFFFFF` with `#E8E0D4` borders
- **Primary accent**: `#D97757` terracotta
- **Positive**: `#4E8A6E` sage green
- **Negative**: `#C2553D` muted red
- **Info**: `#5B7FBA` steel blue

Each tab uses a consistent accent color for its KPI values — terracotta for Pipeline, green for Revenue, teal for Customer, blue for Contacts, amber for Marketing, red for Finance, purple for Activity.
