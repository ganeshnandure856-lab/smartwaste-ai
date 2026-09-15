import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================
# DATABASE CONNECTION
# ============================================

def get_connection():

    if not DATABASE_URL:

        raise Exception(
            "DATABASE_URL is not configured in .env"
        )

    return psycopg2.connect(DATABASE_URL)


# ============================================
# CREATE DATABASE TABLES
# ============================================

def create_database():

    conn = get_connection()

    cursor = conn.cursor()

    # ----------------------------------------
    # DUSTBINS TABLE
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dustbins (

            id SERIAL PRIMARY KEY,

            dustbin_id VARCHAR(100) UNIQUE NOT NULL,

            location VARCHAR(255),

            latitude DOUBLE PRECISION,

            longitude DOUBLE PRECISION,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


    # ----------------------------------------
    # SENSOR READINGS TABLE
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dustbin_readings (

            id SERIAL PRIMARY KEY,

            dustbin_id VARCHAR(100) NOT NULL,

            distance DOUBLE PRECISION,

            fill_level DOUBLE PRECISION,

            status VARCHAR(50),

            temperature DOUBLE PRECISION,

            humidity DOUBLE PRECISION,

            gas_raw DOUBLE PRECISION,

            odor_status VARCHAR(50),

            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


    conn.commit()

    cursor.close()

    conn.close()

    print("Database tables are ready.")


# ============================================
# GET ALL DUSTBINS
# ============================================

def get_all_dustbins():

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    query = """
        SELECT
            d.id,
            d.dustbin_id,
            d.location,
            d.latitude,
            d.longitude,
            d.created_at,

            COALESCE(r.distance, 0)
                AS distance,

            COALESCE(r.fill_level, 0)
                AS fill_level,

            COALESCE(r.status, 'NORMAL')
                AS status,

            COALESCE(r.temperature, 0)
                AS temperature,

            COALESCE(r.humidity, 0)
                AS humidity,

            COALESCE(r.gas_raw, 0)
                AS gas_raw,

            COALESCE(r.odor_status, 'NORMAL')
                AS odor_status,

            r.timestamp

        FROM dustbins d

        LEFT JOIN LATERAL (

            SELECT
                distance,
                fill_level,
                status,
                temperature,
                humidity,
                gas_raw,
                odor_status,
                timestamp

            FROM dustbin_readings

            WHERE dustbin_id = d.dustbin_id

            ORDER BY timestamp DESC, id DESC

            LIMIT 1

        ) r ON TRUE

        ORDER BY d.id ASC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    result = []

    for row in rows:

        row = dict(row)

        if row.get("created_at"):

            row["created_at"] = (
                row["created_at"].isoformat()
            )

        if row.get("timestamp"):

            row["timestamp"] = (
                row["timestamp"].isoformat()
            )

        result.append(row)

    return result


# ============================================
# ADD DUSTBIN
# ============================================

def add_dustbin(data):

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    query = """
        INSERT INTO dustbins (
            dustbin_id,
            location,
            latitude,
            longitude
        )

        VALUES (
            %s,
            %s,
            %s,
            %s
        )

        RETURNING
            id,
            dustbin_id,
            location,
            latitude,
            longitude,
            created_at
    """

    cursor.execute(
        query,
        (
            data.get("dustbin_id"),
            data.get("location"),
            data.get("latitude"),
            data.get("longitude")
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()

    conn.close()

    result = dict(result)

    if result.get("created_at"):

        result["created_at"] = (
            result["created_at"].isoformat()
        )

    return result


# ============================================
# ADD SENSOR READING
# ============================================

def add_reading(data):

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    query = """
        INSERT INTO dustbin_readings (

            dustbin_id,

            distance,

            fill_level,

            status,

            temperature,

            humidity,

            gas_raw,

            odor_status

        )

        VALUES (

            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s

        )

        RETURNING

            id,

            dustbin_id,

            distance,

            fill_level,

            status,

            temperature,

            humidity,

            gas_raw,

            odor_status,

            timestamp
    """

    cursor.execute(
        query,
        (
            data.get("dustbin_id"),
            data.get("distance"),
            data.get("fill_level"),
            data.get("status"),
            data.get("temperature"),
            data.get("humidity"),
            data.get("gas_raw"),
            data.get("odor_status")
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()

    conn.close()

    result = dict(result)

    if result.get("timestamp"):

        result["timestamp"] = (
            result["timestamp"].isoformat()
        )

    return result


# ============================================
# GET READING HISTORY
# ============================================

def get_reading_history(
    dustbin_id,
    hours=24
):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT

            timestamp,

            distance,

            fill_level,

            temperature,

            humidity,

            gas_raw,

            odor_status,

            status

        FROM dustbin_readings

        WHERE dustbin_id = %s

        AND timestamp >=
            NOW() - (%s * INTERVAL '1 hour')

        ORDER BY timestamp ASC
    """

    cursor.execute(
        query,
        (
            dustbin_id,
            hours
        )
    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    history = []

    for row in rows:

        history.append({

            "timestamp":
                row[0].isoformat()
                if row[0]
                else None,

            "distance":
                float(row[1])
                if row[1] is not None
                else 0,

            "fill_level":
                float(row[2])
                if row[2] is not None
                else 0,

            "temperature":
                float(row[3])
                if row[3] is not None
                else 0,

            "humidity":
                float(row[4])
                if row[4] is not None
                else 0,

            "gas_raw":
                float(row[5])
                if row[5] is not None
                else 0,

            "odor_status":
                row[6]
                if row[6]
                else "NORMAL",

            "status":
                row[7]
                if row[7]
                else "NORMAL"
        })

    return history


# ============================================
# BIN ANALYTICS
# ============================================

def get_bin_analytics(dustbin_id):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT

            timestamp,

            fill_level

        FROM dustbin_readings

        WHERE dustbin_id = %s

        ORDER BY timestamp ASC
    """

    cursor.execute(
        query,
        (dustbin_id,)
    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()


    # ----------------------------------------
    # NO DATA
    # ----------------------------------------

    if not rows:

        return {

            "dustbin_id": dustbin_id,

            "readings": 0,

            "current_fill": 0,

            "fill_rate_per_hour": 0,

            "estimated_hours_to_full": None
        }


    # ----------------------------------------
    # CURRENT FILL
    # ----------------------------------------

    current_fill = float(
        rows[-1][1] or 0
    )


    fill_rate = 0


    # ----------------------------------------
    # CALCULATE FILL RATE
    # ----------------------------------------

    if len(rows) >= 2:

        first_time = rows[0][0]

        last_time = rows[-1][0]

        first_fill = float(
            rows[0][1] or 0
        )

        last_fill = float(
            rows[-1][1] or 0
        )


        time_difference = (

            (
                last_time - first_time
            ).total_seconds()

            / 3600
        )


        if time_difference > 0:

            fill_rate = (

                last_fill - first_fill

            ) / time_difference


    # ----------------------------------------
    # ESTIMATE TIME TO FULL
    # ----------------------------------------

    estimated_hours = None


    if (
        fill_rate > 0
        and current_fill < 100
    ):

        remaining = (
            100 - current_fill
        )

        estimated_hours = (
            remaining / fill_rate
        )


    # ----------------------------------------
    # RETURN ANALYTICS
    # ----------------------------------------

    return {

        "dustbin_id": dustbin_id,

        "readings": len(rows),

        "current_fill":
            round(current_fill, 2),

        "fill_rate_per_hour":
            round(fill_rate, 2),

        "estimated_hours_to_full":

            round(
                estimated_hours,
                2
            )

            if estimated_hours is not None
            else None
    }