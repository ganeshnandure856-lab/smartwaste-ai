from flask import (
    Flask,
    jsonify,
    render_template,
    request
)

from flask_cors import CORS

from backend.database import (
    create_database,
    get_all_dustbins,
    add_dustbin,
    add_reading,
    get_reading_history,
    get_bin_analytics
)

import os
import joblib
import pandas as pd


# ============================================
# PATHS
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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

    feature_columns = joblib.load(
        FEATURES_PATH
    )

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


# ============================================
# CORS
# ============================================

CORS(app)


# ============================================
# HOME
# ============================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================
# DASHBOARD
# ============================================

@app.route("/dashboard")
def dashboard():

    return render_template(
        "index.html"
    )


# ============================================
# HEALTH CHECK
# ============================================

@app.route("/api/health")
def health():

    return jsonify({

        "status": "healthy",

        "message":
            "Smart Waste Management System API is running"

    })


# ============================================
# GET ALL DUSTBINS
# ============================================

@app.route(
    "/api/dustbin",
    methods=["GET"]
)
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

@app.route(
    "/api/dustbin",
    methods=["POST"]
)
def create_dustbin():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "Request body is empty"

            }), 400

        if not data.get("dustbin_id"):

            return jsonify({

                "success": False,

                "error":
                    "dustbin_id is required"

            }), 400

        result = add_dustbin(data)

        return jsonify({

            "success": True,

            "message":
                "Dustbin added successfully",

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

@app.route(
    "/api/reading",
    methods=["POST"]
)
def create_reading():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "Request body is empty"

            }), 400

        if not data.get("dustbin_id"):

            return jsonify({

                "success": False,

                "error":
                    "dustbin_id is required"

            }), 400

        result = add_reading(data)

        return jsonify({

            "success": True,

            "message":
                "Sensor reading added successfully",

            "data": result

        }), 201

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================
# ML OVERFLOW PREDICTION
# ============================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict_overflow():

    try:

        if model is None:

            return jsonify({

                "success": False,

                "error":
                    "ML model is not loaded"

            }), 500

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "Request body is empty"

            }), 400

        # Required model features
        input_data = {

            "distance":
                data.get("distance", 0),

            "fill_level":
                data.get("fill_level", 0),

            "hour":
                data.get("hour", 0),

            "day_of_week":
                data.get("day_of_week", 0),

            "previous_fill_level":
                data.get("previous_fill_level", 0),

            "fill_change":
                data.get("fill_change", 0),

            "time_difference_minutes":
                data.get("time_difference_minutes", 0),

            "fill_rate":
                data.get("fill_rate", 0),

            "fill_rate_rolling_mean":
                data.get("fill_rate_rolling_mean", 0),

            "previous_distance":
                data.get("previous_distance", 0),

            "distance_change":
                data.get("distance_change", 0)

        }

        # Create DataFrame
        input_df = pd.DataFrame([
            input_data
        ])

        # Maintain training feature order
        input_df = input_df[
            feature_columns
        ]

        # Handle missing values
        input_df = input_df.fillna(0)

        # Prediction
        prediction = int(
            model.predict(input_df)[0]
        )

        probability = float(
            model.predict_proba(input_df)[0][1]
        )

        return jsonify({

            "success": True,

            "prediction": prediction,

            "overflow_risk":
                "YES" if prediction == 1 else "NO",

            "risk_probability":
                round(probability, 4),

            "risk_percentage":
                round(probability * 100, 2)

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================
# GET READING HISTORY
# ============================================

@app.route(
    "/api/readings/<dustbin_id>",
    methods=["GET"]
)
def reading_history(dustbin_id):

    try:

        history = get_reading_history(
            dustbin_id,
            24
        )

        return jsonify({

            "success": True,

            "dustbin_id":
                dustbin_id,

            "hours": 24,

            "count":
                len(history),

            "data":
                history

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================
# BIN ANALYTICS
# ============================================

@app.route(
    "/api/analytics/<dustbin_id>",
    methods=["GET"]
)
def bin_analytics(dustbin_id):

    try:

        analytics = get_bin_analytics(
            dustbin_id
        )

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

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )