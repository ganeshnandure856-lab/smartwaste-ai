from pathlib import Path

import pandas as pd


# Find the root folder of our project
project_root = Path(__file__).resolve().parents[2]

# Build the dataset path
dataset_path = (
    project_root
    / "data"
    / "raw"
    / "waste_sensor_data.csv"
)

# Read CSV
df = pd.read_csv(dataset_path)

# Display first 5 rows
print("FIRST 5 ROWS")
print(df.head())

print("\n" + "=" * 50)

# Display number of rows and columns
print("DATASET SHAPE")
print(df.shape)

print("\n" + "=" * 50)

# Display column names
print("COLUMNS")
print(df.columns.tolist())
#print("COLUMNS")
#print(df.columns.tolist())

print("\n" + "=" * 50)

print("DATASET INFORMATION")
print(df.info())