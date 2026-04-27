"""Script to run batch predictions against the API using unseen data.

Reads future unseen examples from the CSV, formats the payloads,
and hits the local API endpoint to generate predictions.

Usage:
    python batch_predict.py
"""

import math

import httpx
import pandas as pd


def main():
    api_url = "http://localhost:8000/predict"
    csv_path = "data/future_unseen_examples.csv"

    # API expects these specific fields
    api_fields = [
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "floors",
        "sqft_above",
        "sqft_basement",
        "zipcode",
    ]

    print(f"Loading unseen examples from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}. Are you in the project root?")
        return

    # Ensure zipcode is treated as a string (handling float formatting
    # if pandas inferred float)
    df["zipcode"] = df["zipcode"].astype(str).str.replace(r"\.0$", "", regex=True)

    # Filter to only the fields the API expects
    df = df[api_fields]

    # Convert DataFrame rows to a list of dictionaries
    records = df.to_dict(orient="records")

    print(f"Sending {len(records)} prediction requests to {api_url}...\n")

    success_count = 0
    with httpx.Client(timeout=10.0) as client:
        for i, record in enumerate(records, 1):
            # Replace NaN/math.nan with None so Pydantic accepts it properly as null
            payload = {
                k: (None if isinstance(v, float) and math.isnan(v) else v)
                for k, v in record.items()
            }

            try:
                response = client.post(api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                price = result["predicted_price"]

                # Format output nicely
                print(
                    f"Row {i:3d} | Zipcode: {payload['zipcode']:5s} | Predicted Price: ${price:,.2f}"  # noqa
                )
                success_count += 1
            except httpx.HTTPStatusError as e:
                print(f"Row {i:3d} | Error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                print(f"Row {i:3d} | Failed: {e}")

    print(f"\nCompleted! Successfully predicted {success_count}/{len(records)} rows.")


if __name__ == "__main__":
    main()
