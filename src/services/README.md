# Service Layer (`src/services/`)

This directory contains the business logic, fully decoupled from the API routing layer. This Object-Oriented approach makes the code highly modular, testable, and maintainable.

## Components
*   **`model_service.py` (`ModelService`)**: Encapsulates all file I/O operations. It provides static methods to safely load the pickled model, the feature schema, and the demographic CSV into an O(1) lookup dictionary. It utilizes Python context managers to ensure safe file handling.
*   **`prediction_service.py` (`PredictionService`)**: The core prediction engine. It owns the loaded artifacts and manages the entire pipeline cleanly: 
    1. Validating the input zipcode.
    2. Enriching the base features with demographic data.
    3. Formatting the data for the model and returning the predicted price.
