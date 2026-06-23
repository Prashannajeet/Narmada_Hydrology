from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import analytics, audit, auth, dams, documents, field_inspections, health, mpwrd, risk_register, uploads
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production-ready dam registry APIs for NITA AI Dam Safety Intelligence Platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dams.router, prefix="/api/dams", tags=["dams"])
app.include_router(uploads.router, prefix="/api/dams", tags=["reservoir-upload"])
app.include_router(documents.router, prefix="/api/dams", tags=["documents"])
app.include_router(analytics.router, prefix="/api/analytics/dams", tags=["analytics"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(mpwrd.router, prefix="/api/mpwrd", tags=["mpwrd"])
app.include_router(field_inspections.router, prefix="/api/field-inspections", tags=["field-inspections"])
app.include_router(risk_register.router, prefix="/api/risk-register", tags=["risk-register"])
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
