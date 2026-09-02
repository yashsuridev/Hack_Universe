from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.database import init_db
from app.api import health, projects, scans, scans_2, dependencies, vulnerabilities, sbom, reports
from app.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting SBOM Auditor", version=settings.app_version)
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down SBOM Auditor")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Automated Software Supply Chain Security & SBOM Auditor",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(scans_2.router, prefix="/api")
app.include_router(dependencies.router, prefix="/api")
app.include_router(vulnerabilities.router, prefix="/api")
app.include_router(sbom.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Automated Software Supply Chain Security & SBOM Auditor",
        "docs": "/docs",
        "health": "/api/health",
    }