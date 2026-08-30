import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================================
# SQLITE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

SQLITE_DATABASE = DATA_DIR / "smartwaste.db"


# ============================================================
# CHECK DATABASE TYPE
# ============================================================

def using_postgresql():

    return bool(DATABASE_URL)


# ============================================================
# SQLITE CONNECTION
# ============================================================

def get_sqlite_connection():

    connection = sqlite3.connect(
        SQLITE_DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# POSTGRESQL CONNECTION
# ============================================================

def get_postgres_connection():

    import psycopg2

    connection = psycopg2.connect(
        DATABASE_URL
    )

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    if using_postgresql():

        connection = get_postgres_connection()

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dustbins (

                id SERIAL PRIMARY KEY,

                dustbin_id TEXT UNIQUE NOT NULL,

                location TEXT DEFAULT 'Unknown',

                latitude DOUBLE PRECISION,

                longitude DOUBLE PRECISION,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dustbin_readings (

                id SERIAL PRIMARY KEY,

                dustbin_id TEXT NOT NULL,

                distance DOUBLE PRECISION NOT NULL,

                fill_level DOUBLE PRECISION NOT NULL,

                status TEXT NOT NULL,

                temperature DOUBLE PRECISION,

                humidity DOUBLE PRECISION,

                gas_raw DOUBLE PRECISION,

                odor_status TEXT,

                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (dustbin_id)
                    REFERENCES dustbins(dustbin_id)

            )
        """)

        connection.commit()

        cursor.close()

        connection.close()

        print(
            "Cloud PostgreSQL database initialized successfully!"
        )

    else:

        connection = get_sqlite_connection()

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dustbins (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                dustbin_id TEXT UNIQUE NOT NULL,

                location TEXT DEFAULT 'Unknown',

                latitude REAL,

                longitude REAL,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP

            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dustbin_readings (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                dustbin_id TEXT NOT NULL,

                distance REAL NOT NULL,

                fill_level REAL NOT NULL,

                status TEXT NOT NULL,

                temperature REAL,

                humidity REAL,

                gas_raw REAL,

                odor_status TEXT,

                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (dustbin_id)
                    REFERENCES dustbins(dustbin_id)

            )
        """)

        connection.commit()

        connection.close()

        print(
            "Local SQLite database initialized successfully!"
        )


# ============================================================
# REGISTER DUSTBIN
# ============================================================

def register_dustbin(
    dustbin_id,
    location="Unknown",
    latitude=None,
    longitude=None
):

    if using_postgresql():

        connection = get_postgres_connection()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO dustbins
            (
                dustbin_id,
                location,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (dustbin_id)
            DO NOTHING
        """, (
            dustbin_id,
            location,
            latitude,
            longitude
        ))

        connection.commit()

        cursor.close()

        connection.close()

    else:

        connection = get_sqlite_connection()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO dustbins
            (
                dustbin_id,
                location,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?)
        """, (
            dustbin_id,
            location,
            latitude,
            longitude
        ))

        connection.commit()

        connection.close()


# ============================================================
# SAVE SENSOR READING
# ============================================================

def save_reading(
    dustbin_id,
    distance,
    fill_level,
    status,
    temperature=None,
    humidity=None,
    gas_raw=None,
    odor_status=None
):

    if using_postgresql():

        connection = get_postgres_connection()

        cursor = connection.cursor()

        # Make sure dustbin exists
        cursor.execute("""
            INSERT INTO dustbins
            (
                dustbin_id
            )
            VALUES (%s)
            ON CONFLICT (dustbin_id)
            DO NOTHING
        """, (
            dustbin_id,
        ))

        # Save reading
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
        """, (
            dustbin_id,
            distance,
            fill_level,
            status,
            temperature,
            humidity,
            gas_raw,
            odor_status
        ))

        connection.commit()

        cursor.close()

        connection.close()

    else:

        connection = get_sqlite_connection()

        cursor = connection.cursor()

        # Make sure dustbin exists
        cursor.execute("""
            INSERT OR IGNORE INTO dustbins
            (
                dustbin_id
            )
            VALUES (?)
        """, (
            dustbin_id,
        ))

        # Save reading
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dustbin_id,
            distance,
            fill_level,
            status,
            temperature,
            humidity,
            gas_raw,
            odor_status
        ))

        connection.commit()

        connection.close()


# ============================================================
# GET ALL READINGS
# ============================================================

def get_all_readings():

    if using_postgresql():

        connection = get_postgres_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

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

            FROM dustbin_readings

            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        connection.close()

        return [

            {
                "id": row[0],
                "dustbin_id": row[1],
                "distance": row[2],
                "fill_level": row[3],
                "status": row[4],
                "temperature": row[5],
                "humidity": row[6],
                "gas_raw": row[7],
                "odor_status": row[8],
                "timestamp": str(row[9])
            }

            for row in rows

        ]

    else:

        connection = get_sqlite_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

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

            FROM dustbin_readings

            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()

        connection.close()

        return [

            dict(row)

            for row in rows

        ]


# ============================================================
# GET ALL DUSTBINS
# ============================================================

def get_all_dustbins():

    if using_postgresql():

        connection = get_postgres_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

                dustbin_id,

                location,

                latitude,

                longitude,

                created_at

            FROM dustbins

            ORDER BY dustbin_id
        """)

        rows = cursor.fetchall()

        cursor.close()

        connection.close()

        return [

            {
                "dustbin_id": row[0],
                "location": row[1],
                "latitude": row[2],
                "longitude": row[3],
                "created_at": str(row[4])
            }

            for row in rows

        ]

    else:

        connection = get_sqlite_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

                dustbin_id,

                location,

                latitude,

                longitude,

                created_at

            FROM dustbins

            ORDER BY dustbin_id
        """)

        rows = cursor.fetchall()

        connection.close()

        return [

            dict(row)

            for row in rows

        ]