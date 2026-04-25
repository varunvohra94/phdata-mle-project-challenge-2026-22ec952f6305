def test_health_endpoint(test_client):
    """Test the /health endpoint returns correct status."""
    response = test_client.get("/health")
    assert response.status_code == 200
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "healthy"


def test_predict_endpoint_valid_input(test_client, sample_home_features):
    """Test the /predict endpoint with valid input."""
    response = test_client.post("/predict", json=sample_home_features)
    assert response.status_code == 200
    response_data = response.json()
    assert "predicted_price" in response_data
    assert isinstance(response_data["predicted_price"], float)


def test_predict_endpoint_missing_values(test_client, sample_home_features):
    """
    Test that the /predict endpoint correctly handles missing values via KNNImputer.
    """
    # Introduce missing values for a few features
    sample_home_features["bathrooms"] = None
    sample_home_features["sqft_lot"] = None

    response = test_client.post("/predict", json=sample_home_features)
    assert response.status_code == 200
    response_data = response.json()
    assert "predicted_price" in response_data
    assert isinstance(response_data["predicted_price"], float)


def test_imputation_preserves_non_null(test_client, sample_home_features):
    """
    Test that the KNNImputer step in the pipeline does not alter non-null features.
    """
    import json
    import pickle

    import numpy as np
    import pandas as pd

    with open("model/model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("model/model_features.json") as f:
        features = json.load(f)

    # We will simulate the input DataFrame before and after imputation
    df = pd.DataFrame([sample_home_features])

    demographics = pd.read_csv("data/zipcode_demographics.csv", dtype={"zipcode": str})
    demographic_info = (
        demographics[demographics["zipcode"] == sample_home_features["zipcode"]]
        .drop(columns="zipcode")
        .reset_index(drop=True)
    )
    df = pd.concat([df, demographic_info], axis=1)
    df = df[features]

    # df1 is completely full
    df_full = df.copy()

    # df2 has some missing values
    df_missing = df.copy()
    df_missing.loc[0, "sqft_lot"] = np.nan
    df_missing.loc[0, "bathrooms"] = np.nan

    # The first step in the pipeline is the KNNImputer
    imputer = model.steps[0][1]

    imputed_full = imputer.transform(df_full)
    imputed_missing = imputer.transform(df_missing)

    # Convert back to DataFrame to compare columns
    imputed_full_df = pd.DataFrame(imputed_full, columns=features)
    imputed_missing_df = pd.DataFrame(imputed_missing, columns=features)

    # Assert that the feature 'bedrooms' which was NOT null is identical in both
    assert imputed_full_df.loc[0, "bedrooms"] == imputed_missing_df.loc[0, "bedrooms"]
    # Assert sqft_living is identical
    assert (
        imputed_full_df.loc[0, "sqft_living"]
        == imputed_missing_df.loc[0, "sqft_living"]
    )

    # Ensure missing values were actually imputed
    assert not np.isnan(imputed_missing_df.loc[0, "sqft_lot"])
    assert not np.isnan(imputed_missing_df.loc[0, "bathrooms"])
