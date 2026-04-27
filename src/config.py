"""Centralized application configuration.

All file paths and environment-specific settings live here rather than
being scattered as string literals across the codebase.  Values can be
overridden via environment variables (e.g. MODEL_PATH=/custom/model.pkl).
"""

import logging

from pydantic_settings import BaseSettings


def setup_logging():
    """Configure standard structured logging across the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class Settings(BaseSettings):
    """Application settings loaded from environment with sensible defaults."""

    # Data paths
    sales_data_path: str = "data/kc_house_data.csv"
    demographics_data_path: str = "data/zipcode_demographics.csv"

    # Model artifact paths
    model_path: str = "model/model.pkl"
    model_features_path: str = "model/model_features.json"
    model_output_dir: str = "model"

    # API configuration
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
