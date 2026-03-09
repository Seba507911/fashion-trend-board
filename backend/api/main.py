"""FastAPI 메인 앱."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import brands, products, analysis, runway

app = FastAPI(title="FTIB API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(runway.router, prefix="/api/runway", tags=["runway"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
