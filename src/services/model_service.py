"""Service for loading and providing access to model artifacts."""

import json
import pickle

import pandas as pd


class ModelService:
    """Handles loading model artifacts from disk.

    Provides static methods for loading the trained sklearn pipeline,
    feature list, and demographic lookup data.  Centralizes all file I/O
    that was previously scattered across main.py and endpoints.py.
    """

    @staticmethod
    def load_model(path: str):
        """Load a pickled sklearn model from the given path.

        Args:
            path: Filesystem path to the .pkl model artifact.

        Returns:
            The deserialized sklearn Pipeline object.
        """
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def load_features(path: str) -> list[str]:
        """Load the ordered feature list from a JSON file.

        Args:
            path: Filesystem path to the model_features.json artifact.

        Returns:
            A list of feature column names in the order expected by the model.
        """
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def load_demographics(path: str) -> dict[str, dict]:
        """Load demographic data and convert to an O(1) lookup dictionary.

        Args:
            path: Filesystem path to the zipcode_demographics CSV.

        Returns:
            A dictionary keyed by zipcode string, where each value is a
            dict of demographic attributes.
        """
        demographics = pd.read_csv(path, dtype={"zipcode": str})
        demographics.set_index("zipcode", inplace=True)
        return demographics.to_dict(orient="index")
