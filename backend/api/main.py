"""FastAPI 메인 앱."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import brands, products, analysis, runway, trendflow, trendflow_check, vlm

app = FastAPI(title="FTIB API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(runway.router, prefix="/api/runway", tags=["runway"])
app.include_router(trendflow.router, prefix="/api/trendflow", tags=["trendflow"])
app.include_router(trendflow_check.router, prefix="/api/trendflow-check", tags=["trendflow-check"])
app.include_router(vlm.router, prefix="/api/vlm", tags=["vlm"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
