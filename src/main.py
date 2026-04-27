"""FastAPI application entry point.

Configures the application lifecycle, middleware, and routing.
Model artifacts are loaded once at startup via the service layer.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router as api_router
from config import Settings
from services.model_service import ModelService
from services.prediction_service import PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model artifacts at startup, clean up on shutdown."""
    settings = Settings()

    model = ModelService.load_model(settings.model_path)
    features = ModelService.load_features(settings.model_features_path)
    demographics = ModelService.load_demographics(settings.demographics_data_path)

    app.state.prediction_service = PredictionService(model, features, demographics)

    yield

    app.state.prediction_service = None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
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
