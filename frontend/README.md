# CareerLeap Dashboard Frontend

React + Vite + Recharts dashboard for the CareerLeap cohort economics engine.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies API calls to `http://127.0.0.1:8000`.

Make sure the FastAPI backend is running first.

## Build

```bash
npm run build
```

Static output is written to `dist/`.

## Project Structure

```
src/
├── App.jsx                          # Main dashboard layout and state
├── api.js                           # Fetch wrapper for /api/calculate
├── index.css                        # Global styles
├── main.jsx                         # React entry point
└── components/
    ├── InputForm.jsx                # Cohort assumptions form
    ├── KPICards.jsx                 # Top summary metrics
    ├── CostBreakdownChart.jsx       # Revenue & costs bar chart
    ├── PricingTiersTable.jsx        # Recommended pricing tiers
    ├── SensitivityCharts.jsx        # Fee & cohort size sensitivity lines
    └── AnnualProjection.jsx         # Annual projection summary
```
