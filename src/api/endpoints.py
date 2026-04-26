import json
import pickle

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
def health_check():
    """
    Health check endpoint for container orchestration.
    Returns 200 if API is ready to accept requests.
    """
    return {"status": "healthy"}


@router.post("/predict")
def predict(request: Request, home_features: HomeFeatures):
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


@router.post("/predict/legacy")
def predict_legacy(home_features: HomeFeatures):
    """
    Legacy prediction endpoint that loads everything from disk for every request.
    Preserved specifically for live performance benchmarking and demonstration purposes.
    """
    # Load the model and features
    with open("model/model.pkl", "rb") as model_file:
        model = pickle.load(model_file)

    with open("model/model_features.json") as features_file:
        model_features = json.load(features_file)

    input_data = pd.DataFrame([home_features.model_dump()])

    # Load demographic data
    demographics = pd.read_csv("data/zipcode_demographics.csv", dtype={"zipcode": str})
    demographic_info = (
        demographics[demographics["zipcode"] == home_features.zipcode]
        .drop(columns="zipcode")
        .reset_index(drop=True)
    )

    # Combine input data with demographic data
    input_data = pd.concat([input_data, demographic_info], axis=1)

    # Ensure the input data has the correct features
    input_data = input_data[model_features]

    # Make prediction
    prediction = model.predict(input_data)

    return {"predicted_price": float(prediction[0])}
