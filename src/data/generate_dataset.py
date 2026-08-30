from pathlib import Path

import numpy as np
import pandas as pd


def generate_dataset(n_samples=1000):
    rng = np.random.default_rng(42)

    data = {
        "bin_id": rng.integers(1, 101, n_samples),

        "fill_level": rng.uniform(
            10, 100, n_samples
        ),

        "temperature": rng.uniform(
            20, 40, n_samples
        ),

        "humidity": rng.uniform(
            30, 90, n_samples
        ),

        "waste_generation_rate": rng.uniform(
            5, 50, n_samples
        ),

        "days_since_collection": rng.integers(
            0, 7, n_samples
        ),

        "odor_level": rng.integers(
            0, 6, n_samples
        ),

        "wet_waste_ratio": rng.uniform(
            0, 1, n_samples
        ),
    }

    df = pd.DataFrame(data)

    return df


if __name__ == "__main__":
    df = generate_dataset()

    print(df.head())
    print()
    print("Shape:", df.shape)

    project_root = Path(__file__).resolve().parents[2]

    output_dir = project_root / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "waste_sensor_data.csv"

    df.to_csv(output_path, index=False)

    print(f"Dataset saved successfully to: {output_path}")