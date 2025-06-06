import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.database import init_db
from app.api import upload, employee, scorecard, scorecard_combined, fleet, vehicle_cost, shifts
from app.config import get_settings
from app.utils.logging_config import setup_logging
# from app.utils.cache import setup_cache

# Konfiguration laden
settings = get_settings()

# Logging konfigurieren
logger = setup_logging()

# App definieren
app = FastAPI(
    title="FastAPI Backend",
    description="Backend API für das Mitarbeiter-Management-System",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    # Datenbank initialisieren
    init_db()
    # Cache initialisieren
    # await setup_cache()
    logger.info("Anwendung erfolgreich gestartet")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Anwendung wird beendet")

# Router registrieren
app.include_router(upload.router, prefix=settings.API_V1_PREFIX + "/upload", tags=["Upload"])
app.include_router(employee.router, prefix=settings.API_V1_PREFIX + "/employees", tags=["Employees"])
app.include_router(scorecard.router, prefix=settings.API_V1_PREFIX + "/scorecard", tags=["Scorecard"])
app.include_router(scorecard_combined.router, prefix=settings.API_V1_PREFIX + "/scorecard-combined", tags=["Scorecard Combined"])
app.include_router(fleet.router, prefix=settings.API_V1_PREFIX + "/fleet", tags=["Fleet"])
app.include_router(vehicle_cost.router, prefix=settings.API_V1_PREFIX + "/vehicle-costs", tags=["Vehicle Costs"])
app.include_router(shifts.router, prefix=settings.API_V1_PREFIX + "/shifts", tags=["Shifts"])
