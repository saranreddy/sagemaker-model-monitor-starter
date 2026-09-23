#!/usr/bin/env python3
"""Create baseline statistics and constraints for Model Monitor."""

import sys
from pathlib import Path

from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.s3 import S3Uploader

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config  # noqa: E402


def create_baseline():
    """
    Create baseline statistics and constraints for Model Monitor.

    This script:
    1. Loads baseline data from local file or S3
    2. Uploads baseline data to S3 if needed
    3. Runs a SageMaker Processing job to generate baseline statistics
    4. Saves constraints and statistics to S3
    """
    print("=" * 80)
    print("Creating Model Monitor Baseline")
    print("=" * 80)

    config = load_config()
    print("\nConfiguration:")
    print(f"  Region: {config.aws_region}")
    print(f"  S3 Bucket: {config.s3_bucket}")
    print(f"  Baseline Job Name: {config['baseline_job_name']}")

    baseline_local_path = Path("data/baseline/baseline.csv")
    if not baseline_local_path.exists():
        print(f"\nERROR: Baseline data not found at {baseline_local_path}")
        print("Run the following command to generate baseline data:")
        print("  python src/scripts/create_baseline_data.py")
        sys.exit(1)

    baseline_data_uri = f"s3://{config.s3_bucket}/baseline/baseline.csv"
    baseline_results_uri = f"s3://{config.s3_bucket}/{config['baseline_results_s3_prefix']}"

    print(f"\nUploading baseline data to {baseline_data_uri}...")
    S3Uploader.upload(
        local_path=str(baseline_local_path),
        desired_s3_uri=baseline_data_uri,
    )
    print("Baseline data uploaded successfully")

    print("\nCreating DefaultModelMonitor...")
    monitor = DefaultModelMonitor(
        role=config.sagemaker_role_arn,
        instance_count=config["baseline_instance_count"],
        instance_type=config["baseline_instance_type"],
        max_runtime_in_seconds=config["baseline_max_runtime_seconds"],
    )

    print("\nSuggesting baseline (this will run a SageMaker Processing job)...")
    print(f"  Input: {baseline_data_uri}")
    print(f"  Output: {baseline_results_uri}")
    print(f"  Instance: {config['baseline_instance_type']}")
    print("\nThis may take 5-10 minutes. Monitor progress in the AWS Console:")
    print(f"  SageMaker → Processing → Jobs → {config['baseline_job_name']}")

    try:
        monitor.suggest_baseline(
            baseline_dataset=baseline_data_uri,
            dataset_format={"csv": {"header": False}},
            output_s3_uri=baseline_results_uri,
            job_name=config["baseline_job_name"],
            wait=True,
            logs=True,
        )

        print("\n" + "=" * 80)
        print("Baseline creation completed successfully!")
        print("=" * 80)
        print(f"\nBaseline results saved to: {baseline_results_uri}")
        print("\nNext steps:")
        print("  1. Ensure you have an endpoint deployed (or use the MLOps starter endpoint)")
        print("  2. Run: python scripts/enable_monitoring.py")

    except Exception as e:
        print(f"\nERROR: Baseline job failed: {e}")
        print("\nTroubleshooting:")
        print("  - Check CloudWatch Logs: /aws/sagemaker/ProcessingJobs")
        print("  - Verify IAM role has S3 and SageMaker permissions")
        print("  - Ensure baseline data format is correct (CSV without header)")
        sys.exit(1)


if __name__ == "__main__":
    create_baseline()
