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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dustbins (
            id SERIAL PRIMARY KEY,
            dustbin_id VARCHAR(100) UNIQUE NOT NULL,
            location VARCHAR(255),
            fill_level FLOAT DEFAULT 0,
            temperature FLOAT DEFAULT 0,
            odor FLOAT DEFAULT 0,
            status VARCHAR(50) DEFAULT 'Normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Cloud PostgreSQL database initialized successfully!")


def get_all_dustbins():

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            dustbin_id,
            location,
            fill_level,
            temperature,
            odor,
            status,
            created_at,
            updated_at
        FROM dustbins
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    result = []

    for row in rows:
        row = dict(row)

        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()

        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()

        result.append(row)

    return result


def add_dustbin(data):

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    dustbin_id = data.get("dustbin_id")
    location = data.get("location", "")
    fill_level = data.get("fill_level", 0)
    temperature = data.get("temperature", 0)
    odor = data.get("odor", 0)
    status = data.get("status", "Normal")

    cursor.execute("""
        INSERT INTO dustbins
        (
            dustbin_id,
            location,
            fill_level,
            temperature,
            odor,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (
        dustbin_id,
        location,
        fill_level,
        temperature,
        odor,
        status
    ))

    row = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return dict(row)


def update_dustbin(dustbin_id, data):

    connection = get_postgres_connection()

    cursor = connection.cursor(cursor_factory=RealDictCursor)

    fill_level = data.get("fill_level")
    temperature = data.get("temperature")
    odor = data.get("odor")
    status = data.get("status")

    cursor.execute("""
        UPDATE dustbins
        SET
            fill_level = COALESCE(%s, fill_level),
            temperature = COALESCE(%s, temperature),
            odor = COALESCE(%s, odor),
            status = COALESCE(%s, status),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *
    """, (
        fill_level,
        temperature,
        odor,
        status,
        dustbin_id
    ))

    row = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    if row is None:
        raise Exception("Dustbin not found")

    return dict(row)