import os
import joblib
import pandas as pd
import xgboost as xgb


# Project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "smartwaste_xgb_model.json"
)

THRESHOLD_PATH = os.path.join(
    BASE_DIR,
    "smartwaste_threshold.pkl"
)

FEATURES_PATH = os.path.join(
    BASE_DIR,
    "smartwaste_features.pkl"
)


# Load XGBoost model
model = xgb.XGBClassifier()

model.load_model(MODEL_PATH)


# Load threshold
threshold = joblib.load(
    THRESHOLD_PATH
)


# Load feature list
features = joblib.load(
    FEATURES_PATH
)


def predict_overflow_risk(data):

    df = pd.DataFrame([data])

    # Ensure correct feature order
    df = df[features]

    # Get probability of overflow
    probability = model.predict_proba(df)[0][1]

    # Apply selected threshold
    prediction = int(
        probability >= threshold
    )

    return {
        "overflow_risk": prediction,
        "risk_probability": float(probability)
    }


if __name__ == "__main__":

    sample_data = {
        "fill_level": 78,
        "waste_generation_rate": 32,
        "temperature": 29,
        "humidity": 65,
        "rainfall_mm": 0,
        "wet_waste_ratio": 0.4,
        "odor_level": 3,
        "capacity_liters": 660,
        "population_density": 12000,
        "traffic_level": 3,
        "road_condition": 4,
        "hour": 15,
        "day_of_week": 2
    }

    result = predict_overflow_risk(
        sample_data
    )

    print("\n===== SMARTWASTE PREDICTION =====")

    print(
        "Overflow Risk:",
        result["overflow_risk"]
    )

    print(
        "Risk Probability:",
        result["risk_probability"]
    )