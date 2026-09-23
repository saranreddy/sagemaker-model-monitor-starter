"""Generate baseline dataset for Model Monitor (standalone mode)."""

import argparse
import os

import pandas as pd
from sklearn.datasets import fetch_california_housing


def create_baseline_data(output_dir: str):
    """
    Create a baseline CSV dataset from California Housing data.

    This generates a small, representative dataset that Model Monitor
    will use to establish baseline statistics and constraints.

    Args:
        output_dir: Directory to save the baseline CSV file
    """
    print("Loading California Housing dataset...")
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame

    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    baseline_size = min(1000, len(df))
    baseline_df = df.sample(n=baseline_size, random_state=42)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "baseline.csv")

    print(f"Saving baseline dataset ({baseline_size} rows) to {output_path}")
    baseline_df.to_csv(output_path, index=False, header=False)

    print("Baseline data created successfully")
    print(f"\nFirst few rows (no header, as required by Model Monitor):")
    print(baseline_df.head())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate baseline dataset for SageMaker Model Monitor")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/baseline",
        help="Output directory for baseline data",
    )

    args = parser.parse_args()
    create_baseline_data(args.output_dir)
