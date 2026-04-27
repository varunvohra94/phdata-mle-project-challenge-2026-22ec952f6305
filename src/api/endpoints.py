"""API route definitions.

Endpoints are thin wrappers — all business logic lives in the service layer.
"""

import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from services.prediction_service import PredictionService

logger = logging.getLogger("api.endpoints")
router = APIRouter()


class HomeFeatures(BaseModel):
    """Input schema for the prediction endpoint."""

    bedrooms: int | None = None
    bathrooms: float | None = None
    sqft_living: float | None = None
    sqft_lot: float | None = None
    floors: float | None = None
    sqft_above: float | None = None
    sqft_basement: float | None = None
    zipcode: str


@router.get("/health")
def health_check():
    """Health check endpoint for container orchestration.

    Returns 200 if API is ready to accept requests.
    """
    return {"status": "healthy"}


@router.post("/predict")
def predict(request: Request, home_features: HomeFeatures):
    """Predict house price based on home features and zipcode demographics.

    Delegates all business logic to PredictionService.
    """
    logger.info(f"Received prediction request for zipcode: {home_features.zipcode}")
    logger.debug(f"Input features: {home_features.model_dump(exclude_none=True)}")

    service: PredictionService = request.app.state.prediction_service
    predicted_price = service.predict(home_features.model_dump())

    logger.info(f"Prediction successful. Price: ${predicted_price:,.2f}")
    return {"predicted_price": predicted_price}
