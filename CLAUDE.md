# FTIB — Fashion Trend Intelligence Board

## Quick Start

```bash
# Backend
./venv/bin/python -m uvicorn backend.api.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Crawling
./venv/bin/python scripts/run_crawl.py --brand nike --details
./venv/bin/python scripts/run_crawl.py --list

# Deploy (MUST run from project root, not frontend/)
npx vercel --prod --yes
```

## Project Structure

```
backend/
  api/
    main.py              # FastAPI app
    routes/
      brands.py          # GET /api/brands
      products.py         # GET /api/products
      runway.py           # GET /api/runway
      trendflow.py        # GET /api/trendflow/* (5-stage pipeline)
      analysis.py         # GET /api/analysis/* (graph, kpi, colors)
  crawlers/
    brand_configs.py      # Central registry — add new brands here
    base_crawler.py       # Playwright base class
    platform_crawlers/    # Cafe24, Shopify (config-driven)
    brand_crawlers/       # Custom per-brand crawlers
  db/
    database.py           # DDL + SEED_DATA + init_db_sync()
    ftib.db               # SQLite DB (committed, Vercel reads this)
frontend/
  src/
    pages/                # Runway, TrendFlow, TrendAnalysis, GraphView
    components/           # Sidebar, ProductBoard, ProductCard, ProductDetail
    hooks/useProducts.js  # API hooks (useBrands, useProducts)
scripts/
  run_crawl.py            # Main crawl runner with dedup
  crawl_tagwalk.py        # Runway looks crawler
api/
  index.py                # Vercel serverless entry point
vercel.json               # Vercel build config (frontend + API)
```

## Key Conventions

- Python 3.9: Always use `from __future__ import annotations`
- New brands: Add to `brand_configs.py` + `SEED_DATA` in `database.py`
- Color dedup: `save_products()` auto-merges (brand_id, name, price) groups
- Deploy: Always from project root, never from `frontend/`
- DB: SQLite file committed to git; Vercel reads it read-only

## Data (2026-03-11)

- 11 brands, 2,316 market products
- 38 designers, 3,746 runway looks (SS26 + FW26)
- Blocked: ASICS, Adidas (Akamai WAF)

## Trend Flow Pipeline

| Stage | Name | Data | API Endpoint |
|-------|------|------|-------------|
| 1 | Runway Signal | ✅ Real | /api/trendflow/runway-signals |
| 2 | Expert Report | 🔴 Mock | /api/trendflow/expert-mock |
| 3 | Celebrity | 🔴 Mock | /api/trendflow/celeb-mock |
| 4 | Market Validation | ✅ Real | /api/trendflow/market-validation |
| 5 | Forecast | 🔴 Mock | /api/trendflow/forecast-mock |
