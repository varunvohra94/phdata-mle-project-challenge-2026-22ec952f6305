.PHONY: test-build test-unit test-integration test-all clean run-local stop-local demo-predict batch-predict help

# Build the test Docker image
test-build:
	@echo "--- Timing the build Phase (uv) ---"
	time docker build -f Dockerfile.test -t ml-api-test .

# Run unit tests only (fast, no Docker Compose)
test-unit: test-build
	@echo "--- Timing: Unit test Execution ---"
	time docker run --rm \
		-v $(PWD)/test-results:/app/test-results \
		ml-api-test pytest test/unit -v

# Run integration tests with Docker Compose
test-integration:
	@echo "--- Timing: Full System Integration ---"
	time docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test

# Run all tests (unit + integration)
test-all: test-build
	@echo "Running integration tests..."
	time docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test
	@echo "Running unit tests..."
	time docker run --rm \
		-v $(PWD)/test-results:/app/test-results \
		ml-api-test pytest test/unit -v

# Clean up containers and test artifacts
clean:
	docker-compose -f docker-compose.test.yml down -v
	docker-compose down -v
	rm -rf test-results/*

# Run the API locally for development/demo
run-local:
	@echo "--- Starting Local API and Locust UI via Docker Compose ---"
	docker-compose up --build -d
	@echo "API is running at http://localhost:8000"
	@echo "Locust Load Testing UI is running at http://localhost:8089"

# Stop the local API
stop-local:
	@echo "--- Stopping Local API ---"
	docker-compose down

# Send a sample prediction request with missing values
demo-predict:
	@echo "--- Sending Sample Prediction Request with missing values ---"
	curl -X POST "http://localhost:8000/predict" \
		-H "Content-Type: application/json" \
		-d '{"bedrooms": 4, "bathrooms": null, "sqft_living": 1680, "sqft_lot": null, "floors": 1.5, "sqft_above": 1680, "sqft_basement": 0, "zipcode": "98118"}'
	@echo "\n"

# Run batch predictions against the API using the future unseen examples CSV
batch-predict:
	@echo "--- Running Batch Predictions ---"
	uv run python batch_predict.py

# Display help information
help:
	@echo "Docker-Based Testing Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  test-build        - Build the test Docker image"
	@echo "  test-unit         - Run unit tests only (fast)"
	@echo "  test-integration  - Run integration tests with Docker Compose"
	@echo "  test-all          - Run all tests (unit + integration)"
	@echo "  run-local         - Run the API locally in the background"
	@echo "  stop-local        - Stop the locally running API"
	@echo "  demo-predict      - Send a sample prediction request to the local API"
	@echo "  batch-predict     - Run predictions against data/future_unseen_examples.csv"
	@echo "  clean             - Remove containers and test artifacts"
	@echo "  help              - Display this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make test-unit              # Quick unit tests"
	@echo "  make test-integration       # Full integration tests"
	@echo "  make run-local              # Start the app for live demo"
	@echo "  make demo-predict           # Execute sample prediction"
	@echo "  make batch-predict          # Execute batch predictions from CSV"
	@echo "  make clean                  # Clean up after tests"
