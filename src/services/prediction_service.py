"""Service encapsulating the house price prediction pipeline."""

import logging

import pandas as pd
from fastapi import HTTPException

logger = logging.getLogger("api.prediction_service")


class PredictionService:
    """Encapsulates house price prediction logic.

    Owns the trained model, feature list, and demographic lookup.
    Provides a single `predict()` method that handles the full pipeline:
    validate zipcode → enrich with demographics → run model → return price.
    """

    def __init__(self, model, features: list[str], demographics: dict[str, dict]):
        """Initialize the prediction service with loaded artifacts.

        Args:
            model: A trained sklearn Pipeline object.
            features: Ordered list of feature names expected by the model.
            demographics: Zipcode-keyed dict of demographic attributes.
        """
        self._model = model
        self._features = features
        self._demographics = demographics

    @property
    def model(self):
        """The trained sklearn Pipeline."""
        return self._model

    @property
    def features(self) -> list[str]:
        """The ordered feature list expected by the model."""
        return self._features

    def predict(self, home_features: dict) -> float:
        """Run the full prediction pipeline.

        Args:
            home_features: Dictionary of home attributes including 'zipcode'.

        Returns:
            The predicted house price as a float.

        Raises:
            HTTPException: If the zipcode has no demographic data.
        """
        zipcode = home_features["zipcode"]
        self._validate_zipcode(zipcode)

        logger.debug(f"Enriching features with demographics for zipcode {zipcode}")
        enriched = self._enrich_with_demographics(home_features, zipcode)

        logger.debug("Running model on enriched features...")
        return self._run_model(enriched)

    def _validate_zipcode(self, zipcode: str) -> None:
        """Raise 400 if the zipcode is not in the demographic dataset."""
        if zipcode not in self._demographics:
            logger.warning(
                f"Prediction failed: No demographic data found for zipcode {zipcode}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"No demographic data found for zipcode: {zipcode}",
            )

    def _enrich_with_demographics(self, features: dict, zipcode: str) -> dict:
        """Merge home features with demographic data for the given zipcode.

        Returns a dictionary keyed by the model's expected feature order.
        """
        enriched = {**features}
        enriched.update(self._demographics[zipcode])
        return {feature: enriched.get(feature) for feature in self._features}

    def _run_model(self, enriched_features: dict) -> float:
        """Convert enriched features to a DataFrame and run the model."""
        input_data = pd.DataFrame([enriched_features])
        prediction = self._model.predict(input_data)
        return float(prediction[0])
