from datetime import datetime
import os

import joblib
import pandas as pd

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from algorithms.forecast import (
    estimate_time_to_overflow,
    forecast_fill_level,
    calculate_average_fill_rate
)

from backend.database import (
    create_database,
    get_all_dustbins,
    add_dustbin,
    add_reading,
    get_reading_history,
    get_bin_analytics,
    get_latest_two_readings,
    get_recent_readings
)


# ============================================
# PATHS
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "overflow_model.pkl"
)

FEATURES_PATH = os.path.join(
    BASE_DIR,
    "models",
    "feature_columns.pkl"
)


# ============================================
# LOAD ML MODEL
# ============================================

try:
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)

    print("ML model loaded successfully")

except Exception as e:
    model = None
    feature_columns = None

    print("ML model loading failed:", e)


# ============================================
# FLASK APPLICATION
# ============================================

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)


# ============================================
# HOME
# ============================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# ============================================
# HEALTH CHECK
# ============================================

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "message": "Smart Waste Management System API is running"
    })


# ============================================
# GET ALL DUSTBINS
# ============================================

@app.route("/api/dustbin", methods=["GET"])
def get_dustbins():
    try:
        dustbins = get_all_dustbins()

        return jsonify({
            "success": True,
            "count": len(dustbins),
            "data": dustbins
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# CREATE DUSTBIN
# ============================================

@app.route("/api/dustbin", methods=["POST"])
def create_dustbin():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is empty"
            }), 400

        if not data.get("dustbin_id"):
            return jsonify({
                "success": False,
                "error": "dustbin_id is required"
            }), 400

        result = add_dustbin(data)

        return jsonify({
            "success": True,
            "message": "Dustbin added successfully",
            "data": result
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# ADD SENSOR READING
# ============================================

@app.route("/api/reading", methods=["POST"])
def create_reading():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is empty"
            }), 400

        if not data.get("dustbin_id"):
            return jsonify({
                "success": False,
                "error": "dustbin_id is required"
            }), 400

        result = add_reading(data)

        return jsonify({
            "success": True,
            "message": "Sensor reading added successfully",
            "data": result
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# MANUAL ML OVERFLOW PREDICTION
# ============================================

@app.route("/api/predict", methods=["POST"])
def predict_overflow():
    try:
        if model is None or feature_columns is None:
            return jsonify({
                "success": False,
                "error": "ML model or feature columns not loaded"
            }), 500

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is empty"
            }), 400

        input_data = {
            "distance": data.get("distance", 0),
            "fill_level": data.get("fill_level", 0),
            "hour": data.get("hour", 0),
            "day_of_week": data.get("day_of_week", 0),
            "previous_fill_level": data.get("previous_fill_level", 0),
            "fill_change": data.get("fill_change", 0),
            "time_difference_minutes": data.get(
                "time_difference_minutes", 0
            ),
            "fill_rate": data.get("fill_rate", 0),
            "fill_rate_rolling_mean": data.get(
                "fill_rate_rolling_mean", 0
            ),
            "previous_distance": data.get("previous_distance", 0),
            "distance_change": data.get("distance_change", 0)
        }

        input_df = pd.DataFrame([input_data])
        input_df = input_df[feature_columns]
        input_df = input_df.fillna(0)

        prediction = int(model.predict(input_df)[0])

        probability = float(
            model.predict_proba(input_df)[0][1]
        )

        return jsonify({
            "success": True,
            "prediction": prediction,
            "overflow_risk": "YES" if prediction == 1 else "NO",
            "risk_probability": round(probability, 4),
            "risk_percentage": round(probability * 100, 2)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# LIVE AI PREDICTION
# ============================================

@app.route("/api/predict/<dustbin_id>", methods=["GET"])
def live_predict(dustbin_id):
    try:
        if model is None or feature_columns is None:
            return jsonify({
                "success": False,
                "error": "ML model or feature columns not loaded"
            }), 500

        readings = get_latest_two_readings(dustbin_id)

        if not readings:
            return jsonify({
                "success": False,
                "error": "No sensor readings found"
            }), 404

        latest = readings[0]

        distance = float(latest[0] or 0)
        fill_level = float(latest[1] or 0)
        latest_time = latest[2]

        previous_fill = fill_level
        previous_distance = distance
        fill_change = 0.0
        distance_change = 0.0
        time_difference = 0.0
        fill_rate = 0.0

        if len(readings) >= 2:
            previous = readings[1]

            previous_distance = float(previous[0] or 0)
            previous_fill = float(previous[1] or 0)
            previous_time = previous[2]

            fill_change = fill_level - previous_fill
            distance_change = distance - previous_distance

            if latest_time and previous_time:
                time_difference = (
                    latest_time - previous_time
                ).total_seconds() / 60

                if time_difference >= 1:
                    fill_rate = fill_change / (
                        time_difference / 60
                    )

        fill_change = max(-100, min(100, fill_change))
        distance_change = max(-400, min(400, distance_change))
        fill_rate = max(-100, min(100, fill_rate))

        now = latest_time or datetime.now()

        input_data = {
            "distance": distance,
            "fill_level": fill_level,
            "hour": now.hour,
            "day_of_week": now.weekday(),
            "previous_fill_level": previous_fill,
            "fill_change": fill_change,
            "time_difference_minutes": time_difference,
            "fill_rate": fill_rate,
            "fill_rate_rolling_mean": fill_rate,
            "previous_distance": previous_distance,
            "distance_change": distance_change
        }

        print("\n========================================")
        print("LIVE PREDICTION FEATURES")
        print("========================================")
        print(input_data)

        input_df = pd.DataFrame([input_data])
        input_df = input_df[feature_columns]
        input_df = input_df.fillna(0)

        prediction = int(model.predict(input_df)[0])

        probability = float(
            model.predict_proba(input_df)[0][1]
        )

        return jsonify({
            "success": True,
            "dustbin_id": dustbin_id,
            "fill_level": round(fill_level, 2),
            "prediction": prediction,
            "overflow_risk": "YES" if prediction == 1 else "NO",
            "risk_probability": round(probability, 4),
            "risk_percentage": round(probability * 100, 2)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# GET READING HISTORY
# ============================================

@app.route("/api/readings/<dustbin_id>", methods=["GET"])
def reading_history(dustbin_id):
    try:
        history = get_reading_history(dustbin_id, 24)

        return jsonify({
            "success": True,
            "dustbin_id": dustbin_id,
            "hours": 24,
            "count": len(history),
            "data": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# BIN ANALYTICS
# ============================================

@app.route("/api/analytics/<dustbin_id>", methods=["GET"])
def bin_analytics(dustbin_id):
    try:
        analytics = get_bin_analytics(dustbin_id)

        return jsonify({
            "success": True,
            "data": analytics
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# HISTORICAL AI FORECAST
# ============================================

@app.route("/api/forecast/<dustbin_id>", methods=["GET"])
def forecast_dustbin(dustbin_id):
    try:
        historical_readings = get_recent_readings(
            dustbin_id,
            limit=10
        )

        if not historical_readings:
            return jsonify({
                "success": False,
                "error": "No sensor readings found"
            }), 404

        latest = historical_readings[0]

        current_fill = float(latest[0] or 0)

        previous_fill = current_fill

        if len(historical_readings) >= 2:
            previous_fill = float(
                historical_readings[1][0] or 0
            )

        # Calculate average rate using historical readings
        fill_rate = calculate_average_fill_rate(
            historical_readings
        )

        # Prevent extreme sensor noise
        fill_rate = max(-100, min(100, fill_rate))

        # Forecast after 2 hours
        predicted_fill = forecast_fill_level(
            current_fill,
            fill_rate,
            future_hours=2
        )

        # Estimate time to reach 80%
        time_to_overflow = estimate_time_to_overflow(
            current_fill,
            fill_rate,
            overflow_threshold=80
        )

        # Forecast status message
        if current_fill >= 80:
            forecast_message = (
                "Dustbin has already reached the overflow threshold."
            )

        elif fill_rate <= 0:
            forecast_message = (
                "Fill level is stable or decreasing."
            )

        elif predicted_fill >= 80:
            forecast_message = (
                "Dustbin may reach the overflow threshold "
                "within the next 2 hours."
            )

        else:
            forecast_message = (
                "Dustbin is unlikely to overflow within "
                "the next 2 hours."
            )

        return jsonify({
            "success": True,
            "dustbin_id": dustbin_id,
            "current_fill": round(current_fill, 2),
            "previous_fill": round(previous_fill, 2),
            "fill_rate_per_hour": round(fill_rate, 2),
            "predicted_fill_after_2_hours": predicted_fill,
            "estimated_time_to_80_percent": time_to_overflow,
            "forecast_hours": 2,
            "historical_readings_used": len(
                historical_readings
            ),
            "forecast_message": forecast_message
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# START APPLICATION
# ============================================

if __name__ == "__main__":
    create_database()

    print()
    print("========================================")
    print(" SMART WASTE MANAGEMENT SYSTEM")
    print("========================================")
    print("API running on port 5000")
    print("Dashboard: http://127.0.0.1:5000/dashboard")
    print("========================================")
    print()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )