import joblib
import pandas as pd


# --------------------------------
# 1. File paths
# --------------------------------

MODEL_PATH = "models/overflow_model.pkl"
FEATURES_PATH = "models/feature_columns.pkl"


# --------------------------------
# 2. Load trained model
# --------------------------------

model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURES_PATH)


# --------------------------------
# 3. Sample sensor data
# --------------------------------
# Simulating a dustbin with high fill level

sample_data = {
    "distance": 5.0,
    "fill_level": 95.0,
    "hour": 14,
    "day_of_week": 5,
    "previous_fill_level": 85.0,
    "fill_change": 10.0,
    "time_difference_minutes": 10.0,
    "fill_rate": 1.0,
    "fill_rate_rolling_mean": 0.9,
    "previous_distance": 15.0,
    "distance_change": -10.0
}


# --------------------------------
# 4. Convert data to DataFrame
# --------------------------------

input_data = pd.DataFrame([sample_data])

# Maintain the same feature order used during training
input_data = input_data[features]

# Handle missing values
input_data = input_data.fillna(0)


# --------------------------------
# 5. Make prediction
# --------------------------------

prediction = model.predict(input_data)[0]

probability = model.predict_proba(input_data)[0][1]


# --------------------------------
# 6. Display result
# --------------------------------

print("\n===== SMART WASTE PREDICTION =====")

print("Fill Level:", sample_data["fill_level"], "%")

if prediction == 1:
    print("Overflow Risk: YES")
else:
    print("Overflow Risk: NO")

print("Risk Probability:", round(probability, 4))

print("Risk Percentage:", round(probability * 100, 2), "%")

print("==================================")