import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE = BASE_DIR / "data" / "smartwaste.db"

FEATURE_DIR = BASE_DIR / "data" / "processed"

FEATURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = FEATURE_DIR / "dustbin_features.csv"


# ============================================================
# LOAD DATABASE DATA
# ============================================================

def load_readings():

    connection = sqlite3.connect(DATABASE)

    query = """
        SELECT
            id,
            dustbin_id,
            distance,
            fill_level,
            status,
            timestamp
        FROM dustbin_readings
        ORDER BY dustbin_id, timestamp
    """

    dataframe = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return dataframe


# ============================================================
# BUILD FEATURES
# ============================================================

def build_features(dataframe):

    if dataframe.empty:

        print("No sensor readings found.")

        return dataframe


    # --------------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------------

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"]
    )


    # --------------------------------------------------------
    # Sort data
    # --------------------------------------------------------

    dataframe = dataframe.sort_values(
        [
            "dustbin_id",
            "timestamp"
        ]
    ).reset_index(drop=True)


    # --------------------------------------------------------
    # Time features
    # --------------------------------------------------------

    dataframe["hour"] = (
        dataframe["timestamp"].dt.hour
    )

    dataframe["day_of_week"] = (
        dataframe["timestamp"].dt.dayofweek
    )


    # --------------------------------------------------------
    # Previous fill level
    # --------------------------------------------------------

    dataframe["previous_fill_level"] = (
        dataframe
        .groupby("dustbin_id")["fill_level"]
        .shift(1)
    )


    # --------------------------------------------------------
    # Fill level change
    # --------------------------------------------------------

    dataframe["fill_change"] = (
        dataframe["fill_level"]
        -
        dataframe["previous_fill_level"]
    )


    # --------------------------------------------------------
    # Time difference
    # --------------------------------------------------------

    dataframe["time_difference_minutes"] = (

        dataframe["timestamp"]

        -
        dataframe
        .groupby("dustbin_id")["timestamp"]
        .shift(1)

    ).dt.total_seconds() / 60


    # --------------------------------------------------------
    # Fill rate
    # --------------------------------------------------------

    dataframe["fill_rate"] = (

        dataframe["fill_change"]

        /
        dataframe["time_difference_minutes"]

    )


    # Avoid infinity
    dataframe["fill_rate"] = (
        dataframe["fill_rate"]
        .replace(
            [float("inf"), float("-inf")],
            0
        )
        .fillna(0)
    )


    # --------------------------------------------------------
    # Rolling average fill
    # --------------------------------------------------------

    dataframe["fill_rate_rolling_mean"] = (

        dataframe
        .groupby("dustbin_id")["fill_rate"]
        .transform(
            lambda x:
            x.rolling(
                window=3,
                min_periods=1
            ).mean()
        )

    )


    # --------------------------------------------------------
    # Distance change
    # --------------------------------------------------------

    dataframe["previous_distance"] = (

        dataframe
        .groupby("dustbin_id")["distance"]
        .shift(1)

    )


    dataframe["distance_change"] = (

        dataframe["distance"]
        -
        dataframe["previous_distance"]

    )


    # --------------------------------------------------------
    # Clean missing values
    # --------------------------------------------------------

    dataframe = dataframe.fillna(0)


    return dataframe


# ============================================================
# SAVE FEATURES
# ============================================================

def save_features(dataframe):

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Features saved successfully!")
    print()
    print(
        f"File: {OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==========================================")
    print("       SMART WASTE FEATURE ENGINEERING")
    print("==========================================")
    print()


    # Load readings

    dataframe = load_readings()


    print(
        f"Readings found: {len(dataframe)}"
    )


    # Build features

    dataframe = build_features(
        dataframe
    )


    if dataframe.empty:

        return


    # Save

    save_features(
        dataframe
    )


    print()
    print("Feature engineering completed!")
    print()


if __name__ == "__main__":

    main()