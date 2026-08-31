from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from backend.database import (
    create_database,
    get_all_dustbins,
    add_dustbin,
    add_reading
)

import os


# ==========================================
# FLASK APP
# ==========================================

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "healthy",
        "message": "Smart Waste Management System API is running"
    })


# ==========================================
# GET ALL DUSTBINS
# ==========================================

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


# ==========================================
# ADD DUSTBIN
# ==========================================

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


# ==========================================
# ADD SENSOR READING
# ==========================================

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


# ==========================================
# STARTUP
# ==========================================

if __name__ == "__main__":

    create_database()

    print("")
    print("==========================================")
    print("     SMART WASTE MANAGEMENT SYSTEM")
    print("==========================================")
    print("Server starting...")
    print("")
    print("Dashboard:")
    print("http://127.0.0.1:5000/dashboard")
    print("")
    print("API:")
    print("http://127.0.0.1:5000/api/dustbin")
    print("")
    print("Reading API:")
    print("http://127.0.0.1:5000/api/reading")
    print("")
    print("Health:")
    print("http://127.0.0.1:5000/api/health")
    print("==========================================")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )