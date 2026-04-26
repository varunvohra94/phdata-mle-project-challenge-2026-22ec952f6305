import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class HomeFeatures(BaseModel):
    bedrooms: int | None = None
    bathrooms: float | None = None
    sqft_living: float | None = None
    sqft_lot: float | None = None
    floors: float | None = None
    sqft_above: float | None = None
    sqft_basement: float | None = None
    zipcode: str


@router.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration.
    Returns 200 if API is ready to accept requests.
    """
    return {"status": "healthy"}


@router.post("/predict")
async def predict(request: Request, home_features: HomeFeatures):
    # Access artifacts from application state loaded during lifespan
    model = request.app.state.model
    model_features = request.app.state.features
    demographics = request.app.state.demographics

    zipcode = home_features.zipcode
    if zipcode not in demographics:
        raise HTTPException(
            status_code=400, detail=f"No demographic data found for zipcode: {zipcode}"
        )

    # Convert incoming payload to a dictionary
    input_dict = home_features.model_dump()

    # O(1) dictionary lookup to merge demographic data instantly
    input_dict.update(demographics[zipcode])

    # Construct the final row matching the exact feature order expected by the model
    row = {feature: input_dict.get(feature) for feature in model_features}

    # Convert to DataFrame (or numpy array) for the scikit-learn pipeline
    input_data = pd.DataFrame([row])

    # Make prediction
    prediction = model.predict(input_data)

    return {"predicted_price": float(prediction[0])}
