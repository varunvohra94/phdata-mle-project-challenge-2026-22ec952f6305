# API Layer (`src/api/`)

This directory defines the HTTP routing interface for the application. It acts as the bridge between incoming client requests and our backend Object-Oriented service layer.

## Performance Improvements

Previously, the prediction endpoints suffered from severe performance bottlenecks because they were loading the model (`pickle.load`), features (`json.load`), and demographic data (`pd.read_csv`) directly from the disk **on every single request**.

### The Solution:
1.  **Stateful Lifespan**: Artifacts are now loaded into memory exactly once during application startup via FastAPI's `lifespan` context manager in `main.py`.
2.  **O(1) Lookups**: Demographic data is pre-processed into a Python dictionary keyed by zipcode during startup. This turns an expensive pandas DataFrame filter operation into an instant, sub-millisecond hash map lookup.
3.  **Service Delegation**: The endpoint simply retrieves the `PredictionService` from the initialized `request.app.state` and delegates the data, avoiding any heavy computation or I/O at the API layer.

## Components
*   **`endpoints.py`**: Contains the `/predict` POST route. By migrating the heavy lifting to the `PredictionService`, this file is now a clean, "thin wrapper". It is solely responsible for receiving the `HomeFeatures` Pydantic payload, passing it to the service, logging the event, and returning the JSON response.
