"""FastAPI application entry point.

Configures the application lifecycle, middleware, and routing.
Model artifacts are loaded once at startup via the service layer.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router as api_router
from config import Settings, setup_logging
from services.model_service import ModelService
from services.prediction_service import PredictionService

setup_logging()
logger = logging.getLogger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model artifacts at startup, clean up on shutdown."""
    logger.info("Initializing FastAPI application...")
    settings = Settings()

    logger.info(f"Loading model artifact from: {settings.model_path}")
    model = ModelService.load_model(settings.model_path)

    logger.info(f"Loading feature list from: {settings.model_features_path}")
    features = ModelService.load_features(settings.model_features_path)

    logger.info(f"Loading demographics from: {settings.demographics_data_path}")
    demographics = ModelService.load_demographics(settings.demographics_data_path)
    logger.info(f"Successfully loaded demographics for {len(demographics)} zipcodes.")

    app.state.prediction_service = PredictionService(model, features, demographics)
    logger.info("Application startup complete. Ready to serve predictions.")

    yield

    logger.info("Shutting down application...")
    app.state.prediction_service = None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log the request if it's not the health check spam from Docker
    if request.url.path != "/health":
        logger.info(
            f"Processed {request.method} {request.url.path} in {process_time:.4f}s "
            f"- Status: {response.status_code}"
        )

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
