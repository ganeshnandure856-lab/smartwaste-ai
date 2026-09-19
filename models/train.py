import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# 1. Load dataset
# -----------------------------

DATA_PATH = "data/processed/dustbin_features.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully")
print("Dataset shape:", df.shape)


# -----------------------------
# 2. Create target column
# -----------------------------
# 1 = Overflow risk
# 0 = No overflow risk
#
# Demo rule:
# Fill level >= 80 means overflow risk

df["overflow_risk"] = (df["fill_level"] >= 80).astype(int)


# -----------------------------
# 3. Select features
# -----------------------------

features = [
    "distance",
    "fill_level",
    "hour",
    "day_of_week",
    "previous_fill_level",
    "fill_change",
    "time_difference_minutes",
    "fill_rate",
    "fill_rate_rolling_mean",
    "previous_distance",
    "distance_change"
]

X = df[features]
y = df["overflow_risk"]


# -----------------------------
# 4. Handle missing values
# -----------------------------

X = X.fillna(0)


# -----------------------------
# 5. Split dataset
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----------------------------
# 6. Train model
# -----------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# -----------------------------
# 7. Evaluate model
# -----------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, predictions))


# -----------------------------
# 8. Save model
# -----------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/overflow_model.pkl")

joblib.dump(features, "models/feature_columns.pkl")

print("\nModel saved successfully!")
print("Location: models/overflow_model.pkl")