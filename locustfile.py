import random

from locust import HttpUser, between, task


class HousePriceUser(HttpUser):
    # Wait time between requests for each simulated user
    wait_time = between(0.1, 0.5)

    @task(3)
    def predict_price(self):
        # Generate a semi-random realistic payload
        payload = {
            "bedrooms": random.choice([2, 3, 4, 5]),
            "bathrooms": random.choice([1.0, 2.0, 2.5, None]),
            "sqft_living": random.randint(1000, 3000),
            "sqft_lot": random.choice([5000, 8000, 10000, None]),
            "floors": random.choice([1.0, 1.5, 2.0]),
            "sqft_above": random.randint(1000, 2500),
            "sqft_basement": random.choice([0, 500, 800]),
            "zipcode": random.choice(["98118", "98115", "98030", "98005", "98028"]),
        }

        self.client.post("/predict", json=payload)

    @task(3)
    def predict_legacy_price(self):
        # Generate a semi-random realistic payload for the legacy endpoint
        payload = {
            "bedrooms": random.choice([2, 3, 4, 5]),
            "bathrooms": random.choice([1.0, 2.0, 2.5, None]),
            "sqft_living": random.randint(1000, 3000),
            "sqft_lot": random.choice([5000, 8000, 10000, None]),
            "floors": random.choice([1.0, 1.5, 2.0]),
            "sqft_above": random.randint(1000, 2500),
            "sqft_basement": random.choice([0, 500, 800]),
            "zipcode": random.choice(["98118", "98115", "98030", "98005", "98028"]),
        }

        self.client.post("/predict/legacy", json=payload)

    @task(1)
    def health_check(self):
        self.client.get("/health")
