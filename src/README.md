# Source Code (`src/`)

This directory contains the core application code for the FastAPI server and central configuration.

## Components
*   **`main.py`**: The application entry point. It manages the `lifespan` (startup/shutdown events) to load heavy ML artifacts into memory exactly once. It also defines middleware for request logging and process time tracking.
*   **`config.py`**: Centralized configuration management using `pydantic-settings`. All file paths, host, port, and logging configurations (`setup_logging()`) are defined here, making the system easily configurable via environment variables and eliminating scattered, hardcoded strings.
