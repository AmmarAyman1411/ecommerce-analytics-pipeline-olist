# Pipeline Architecture

High-level view of the end-to-end analytics pipeline for the Olist e-commerce project.

---

## Overview

```
Raw data (CSV)  →  Cleaned tables  →  EDA & KPIs  →  Power BI mart  →  Dashboard
     (Kaggle)         (processed/)      (notebooks)     (powerbi/)       (Power BI)
```

---

## Stages

### 1. Data ingestion and cleaning

- **Input:** Olist CSVs in `data/raw/`.
- **Process:** Notebook `01_data_loading_and_cleaning.ipynb` — load, standardize column names, parse dates, remove duplicates.
- **Output:** `data/processed/*_clean.csv`.

### 2. Exploratory data analysis (EDA) and KPIs

- **Input:** Cleaned tables from `data/processed/`.
- **Process:** Notebook `02_eda_and_kpis.ipynb` — merge tables, compute KPIs, visualizations.
- **Output:** Insights; see `docs/kpi_definitions.md` and `docs/insights_report.md`.

### 3. Power BI mart build

- **Input:** `data/processed/*_clean.csv`.
- **Process:** Script `src/build_powerbi_mart.py` — aggregate revenue, delivery metrics, build fact/dim tables and dim_date.
- **Output:** `data/powerbi/*.csv` (star-schema style).

### 4. Dashboard (Power BI)

- **Input:** `data/powerbi/*.csv` loaded into Power BI Desktop.
- **Process:** Power Query (types, order_purchase_date), Model (relationships, date table), DAX measures, report pages.
- **Output:** `powerbi/ecommerce_dashboard.pbix` and screenshots.

---

## Data flow (simplified)

- orders_clean + payments_clean → fact_orders (revenue, delivery metrics)
- order_items_clean → fact_order_items
- customers_clean → dim_customers; products_clean → dim_products; sellers_clean → dim_sellers
- reviews_clean + fact_orders → fact_reviews (with delivery context)
- fact_orders date range → dim_date

---

## Dependencies

- Phase 1 (cleaning) must complete before Phase 2 and Phase 3.
- Mart script must run before Power BI uses the mart CSVs.
- Power BI only needs the mart CSVs.
