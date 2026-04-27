"""Model training script.

Trains a KNN-based house price prediction pipeline and exports
the model artifact and feature list to disk.

Usage:
    python create_model.py
"""

import json
import pathlib

import pandas as pd
from sklearn import model_selection, neighbors, pipeline, preprocessing
from sklearn.impute import KNNImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error


class ModelTrainer:
    """Encapsulates the model training lifecycle.

    Handles data loading, pipeline construction, training, evaluation,
    and artifact export as a single cohesive unit.
    """

    SALES_COLUMN_SELECTION = [
        "price",
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "floors",
        "sqft_above",
        "sqft_basement",
        "zipcode",
    ]

    def __init__(
        self,
        sales_path: str = "data/kc_house_data.csv",
        demographics_path: str = "data/zipcode_demographics.csv",
        output_dir: str = "model",
    ):
        """Initialize the trainer with data and output paths.

        Args:
            sales_path: Path to CSV file with home sale data.
            demographics_path: Path to CSV file with zipcode demographics.
            output_dir: Directory where model artifacts will be saved.
        """
        self._sales_path = sales_path
        self._demographics_path = demographics_path
        self._output_dir = pathlib.Path(output_dir)

    def load_data(self) -> tuple[pd.DataFrame, pd.Series]:
        """Load and merge sales and demographic data.

        Returns:
            Tuple of (features DataFrame, target Series).
        """
        data = pd.read_csv(
            self._sales_path,
            usecols=self.SALES_COLUMN_SELECTION,
            dtype={"zipcode": str},
        )
        demographics = pd.read_csv(self._demographics_path, dtype={"zipcode": str})

        merged = data.merge(demographics, how="left", on="zipcode").drop(
            columns="zipcode"
        )
        y = merged.pop("price")
        return merged, y

    def build_pipeline(self) -> pipeline.Pipeline:
        """Construct the sklearn pipeline.

        Returns:
            An unfitted Pipeline with KNNImputer, RobustScaler,
            and KNeighborsRegressor stages.
        """
        return pipeline.make_pipeline(
            KNNImputer(n_neighbors=5, weights="distance"),
            preprocessing.RobustScaler(),
            neighbors.KNeighborsRegressor(),
        )

    def train(
        self, model: pipeline.Pipeline, x_train: pd.DataFrame, y_train: pd.Series
    ) -> pipeline.Pipeline:
        """Fit the pipeline on training data.

        Args:
            model: An unfitted sklearn Pipeline.
            x_train: Training feature DataFrame.
            y_train: Training target Series.

        Returns:
            The fitted Pipeline.
        """
        return model.fit(x_train, y_train)

    def evaluate(
        self, model: pipeline.Pipeline, x_test: pd.DataFrame, y_test: pd.Series
    ) -> dict[str, float]:
        """Evaluate the fitted model on the holdout test set.

        Args:
            model: A fitted sklearn Pipeline.
            x_test: Test feature DataFrame.
            y_test: Test target Series.

        Returns:
            Dictionary with RMSE, MAE, and R² metrics.
        """
        predictions = model.predict(x_test)
        metrics = {
            "rmse": root_mean_squared_error(y_test, predictions),
            "mae": mean_absolute_error(y_test, predictions),
            "r2": r2_score(y_test, predictions),
        }
        return metrics

    def export(self, model: pipeline.Pipeline, feature_list: list[str]) -> None:
        """Save model artifacts to the output directory.

        Args:
            model: The fitted sklearn Pipeline to serialize.
            feature_list: Ordered list of feature column names.
        """
        import pickle

        self._output_dir.mkdir(exist_ok=True)

        model_path = self._output_dir / "model.pkl"
        features_path = self._output_dir / "model_features.json"

        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        with open(features_path, "w") as f:
            json.dump(feature_list, f)

    def run(self) -> None:
        """Execute the full training lifecycle."""
        x, y = self.load_data()
        x_train, x_test, y_train, y_test = model_selection.train_test_split(
            x, y, random_state=42
        )

        model = self.build_pipeline()
        model = self.train(model, x_train, y_train)

        metrics = self.evaluate(model, x_test, y_test)
        print(f"RMSE: {metrics['rmse']:.2f}")
        print(f"MAE:  {metrics['mae']:.2f}")
        print(f"R²:   {metrics['r2']:.4f}")

        self.export(model, list(x_train.columns))
        print(f"Model exported to {self._output_dir}/")


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
