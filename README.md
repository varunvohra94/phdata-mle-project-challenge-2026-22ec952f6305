# Housing Price Prediction API 

This project implements a RESTful API using FastAPI to serve a machine learning model for predicting home prices based on real estate features and demographic data. 

The system has been heavily refactored to use an **Object-Oriented Architecture**, centralized configuration, structured logging, and robust testing to adhere to software engineering and MLOps best practices.

## 🏗️ Project Architecture

We have modularized the system into distinct domains. See the detailed documentation inside each directory to understand the design choices and improvements:

*   [`src/README.md`](src/README.md): Core application logic and configuration.
*   [`src/api/README.md`](src/api/README.md): API routing and endpoints (includes details on **performance improvements**).
*   [`src/services/README.md`](src/services/README.md): Business logic layer (Model & Prediction services).
*   [`model/README.md`](model/README.md): ML artifacts and training pipeline (includes details on **KNN Imputation**).

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   [uv](https://github.com/astral-sh/uv) (An extremely fast Python package installer and resolver)
*   Python 3.13+

### 1. Local Development Setup
Clone the repository and install dependencies using `uv`:
```bash
git clone <repository-url>
cd mle-project-challenge-2026
uv sync
```

### 2. Train the Model
Before running the API, you need to generate the model artifacts (`model.pkl` and `model_features.json`).
```bash
uv run python create_model.py
```
*This script will load the data, handle missing values via KNN Imputation, train the model, evaluate it on a holdout test set, and export the artifacts to the `model/` directory.*

### 3. Run the API (Live Demo)
Start the FastAPI application and Locust load testing UI via Docker Compose:
```bash
make run-local
```
*   **API**: `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`)
*   **Locust UI**: `http://localhost:8089`

### 4. Test Predictions
You can test the system in two ways:

**Single Request:**
```bash
make demo-predict
```
*Sends a sample payload (with missing values) via `curl` to demonstrate the model's robustness.*

**Batch Prediction:**
```bash
make batch-predict
```
*Executes `batch_predict.py`, which reads unseen data from `data/future_unseen_examples.csv` and iteratively queries the API. This is excellent for demonstrating logging and latency.*

### 5. Stop the System
```bash
make stop-local
```

## 🧪 Testing

We use `pytest` for unit testing the API and its components. The tests use the FastAPI `TestClient` and leverage the OOP service layer.

Run unit tests locally (builds a test Docker image and runs the suite):
```bash
make test-unit
```

## 📜 Logging & Observability

The application uses structured Python logging. When running `make run-local`, `make batch-predict`, or training the model, you will see a detailed, microsecond-accurate narrative of the system's execution directly in the console. This includes model loading times, data enrichment steps, and request processing metrics.