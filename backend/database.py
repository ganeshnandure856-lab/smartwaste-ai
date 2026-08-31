import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_postgres_connection():

    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set")

    return psycopg2.connect(DATABASE_URL)


def create_database():

    connection = get_postgres_connection()
    cursor = connection.cursor()

    # Dustbin master table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dustbins (
            id SERIAL PRIMARY KEY,
            dustbin_id VARCHAR(100) UNIQUE NOT NULL,
            location VARCHAR(255),
            latitude FLOAT,
            longitude FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sensor readings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dustbin_readings (
            id SERIAL PRIMARY KEY,
            dustbin_id VARCHAR(100) NOT NULL,
            distance FLOAT,
            fill_level FLOAT,
            status VARCHAR(50),
            temperature FLOAT,
            humidity FLOAT,
            gas_raw FLOAT,
            odor_status VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("PostgreSQL database initialized successfully!")


def get_all_dustbins():

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT
            d.id,
            d.dustbin_id,
            d.location,
            d.latitude,
            d.longitude,
            d.created_at,

            r.distance,
            r.fill_level,
            r.status,
            r.temperature,
            r.humidity,
            r.gas_raw,
            r.odor_status,
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
            FROM dustbin_readings r
            WHERE r.dustbin_id = d.dustbin_id
            ORDER BY r.timestamp DESC
            LIMIT 1
        ) r ON TRUE

        ORDER BY d.id ASC
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    result = []

    for row in rows:

        row = dict(row)

        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()

        if row.get("timestamp"):
            row["timestamp"] = row["timestamp"].isoformat()

        result.append(row)

    return result


def add_dustbin(data):

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    dustbin_id = data.get("dustbin_id")
    location = data.get("location", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    cursor.execute("""
        INSERT INTO dustbins
        (
            dustbin_id,
            location,
            latitude,
            longitude
        )
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """, (
        dustbin_id,
        location,
        latitude,
        longitude
    ))

    row = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return dict(row)


def add_reading(data):

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        INSERT INTO dustbin_readings
        (
            dustbin_id,
            distance,
            fill_level,
            status,
            temperature,
            humidity,
            gas_raw,
            odor_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (
        data.get("dustbin_id"),
        data.get("distance"),
        data.get("fill_level"),
        data.get("status"),
        data.get("temperature"),
        data.get("humidity"),
        data.get("gas_raw"),
        data.get("odor_status")
    ))

    row = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return dict(row)