from pathlib import Path

from flask import Flask, jsonify, request, render_template

from database import (
    create_database,
    get_all_readings,
    save_reading,
    register_dustbin
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

create_database()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Waste Management</title>
    </head>

    <body>

        <h1>♻️ Smart Waste Management System</h1>

        <p>Cloud server is running successfully.</p>

        <p>
            <a href="/dashboard">
                Open Dashboard
            </a>
        </p>

    </body>
    </html>
    """


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    return render_template("index.html")


# ============================================================
# RECEIVE DATA FROM ESP32
# ============================================================

@app.route(
    "/api/dustbin",
    methods=["POST"]
)
def receive_dustbin_data():

    try:

        data = request.get_json()


        # ----------------------------------------------------
        # CHECK JSON
        # ----------------------------------------------------

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No JSON data received"

            }), 400


        print()
        print(
            "=========================================="
        )

        print(
            "       DUSTBIN DATA RECEIVED"
        )

        print(
            "=========================================="
        )


        print(data)


        # ----------------------------------------------------
        # DUSTBIN ID
        # ----------------------------------------------------

        dustbin_id = data.get(
            "dustbin_id",
            "BIN001"
        )


        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        distance = float(
            data.get(
                "distance",
                0
            )
        )


        # ----------------------------------------------------
        # FILL LEVEL
        # ----------------------------------------------------

        fill_level = float(
            data.get(
                "fill_level",
                0
            )
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = data.get(
            "status",
            "EMPTY"
        )


        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        temperature = data.get(
            "temperature"
        )


        if temperature is not None:

            temperature = float(
                temperature
            )


        # ----------------------------------------------------
        # HUMIDITY
        # ----------------------------------------------------

        humidity = data.get(
            "humidity"
        )


        if humidity is not None:

            humidity = float(
                humidity
            )


        # ----------------------------------------------------
        # GAS
        # ----------------------------------------------------

        gas_raw = data.get(
            "gas_raw"
        )


        if gas_raw is not None:

            gas_raw = float(
                gas_raw
            )


        # ----------------------------------------------------
        # ODOR
        # ----------------------------------------------------

        odor_status = data.get(
            "odor_status",
            "NORMAL"
        )


        # ----------------------------------------------------
        # REGISTER DUSTBIN
        # ----------------------------------------------------

        register_dustbin(
            dustbin_id
        )


        # ----------------------------------------------------
        # SAVE SENSOR READING
        # ----------------------------------------------------

        save_reading(

            dustbin_id,

            distance,

            fill_level,

            status,

            temperature,

            humidity,

            gas_raw,

            odor_status

        )


        # ----------------------------------------------------
        # CONSOLE
        # ----------------------------------------------------

        print(
            "Saved successfully!"
        )

        print(
            "Bin:",
            dustbin_id
        )

        print(
            "Distance:",
            round(distance, 1),
            "cm"
        )

        print(
            "Fill Level:",
            round(fill_level, 1),
            "%"
        )

        print(
            "Status:",
            status
        )

        print(
            "Temperature:",
            temperature
        )

        print(
            "Humidity:",
            humidity
        )

        print(
            "Gas Raw:",
            gas_raw
        )

        print(
            "Odor:",
            odor_status
        )

        print(
            "=========================================="
        )


        # ----------------------------------------------------
        # RESPONSE TO ESP32
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Dustbin data saved successfully",

            "dustbin_id":
                dustbin_id

        }), 200


    except Exception as e:

        print()

        print(
            "ERROR RECEIVING DATA:"
        )

        print(
            str(e)
        )


        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ============================================================
# GET DUSTBIN DATA
# ============================================================

@app.route(
    "/api/dustbin",
    methods=["GET"]
)
def get_dustbin_data():

    try:

        readings = get_all_readings()


        return jsonify({

            "success": True,

            "data": readings

        }), 200


    except Exception as e:

        print(
            "ERROR GETTING DATA:",
            str(e)
        )


        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health_check():

    return jsonify({

        "success": True,

        "status": "online",

        "message":
            "Smart Waste Management API is running"

    }), 200


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        "     SMART WASTE MANAGEMENT SYSTEM"
    )

    print(
        "=========================================="
    )

    print(
        "Server starting..."
    )

    print()

    print(
        "Dashboard:"
    )

    print(
        "http://127.0.0.1:5000/dashboard"
    )

    print()

    print(
        "API:"
    )

    print(
        "http://127.0.0.1:5000/api/dustbin"
    )

    print()

    print(
        "Health:"
    )

    print(
        "http://127.0.0.1:5000/api/health"
    )

    print()

    print(
        "=========================================="
    )


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )