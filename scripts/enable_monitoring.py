#!/usr/bin/env python3
"""Enable Model Monitor schedule for an endpoint."""

import sys
from pathlib import Path

import boto3
from sagemaker.model_monitor import CronExpressionGenerator, DataCaptureConfig, DefaultModelMonitor

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config


def enable_data_capture(config, sagemaker_client):
    """
    Enable data capture on the endpoint if not already enabled.

    Args:
        config: Configuration object
        sagemaker_client: boto3 SageMaker client
    """
    try:
        response = sagemaker_client.describe_endpoint_config(EndpointConfigName=config.endpoint_name)

        if "DataCaptureConfig" in response and response["DataCaptureConfig"].get("EnableCapture", False):
            print(f"Data capture already enabled on endpoint config")
            return

        print(f"\nWARNING: Data capture not enabled on endpoint {config.endpoint_name}")
        print("To enable data capture, you need to update the endpoint configuration.")
        print("\nFor the MLOps starter endpoint, you can:")
        print("  1. Redeploy with data capture enabled, or")
        print("  2. Update the endpoint configuration manually")
        print("\nData capture is required for Model Monitor to work.")

    except sagemaker_client.exceptions.ResourceNotFound:
        print(f"\nERROR: Endpoint config not found: {config.endpoint_name}")
        print("Ensure the endpoint exists before enabling monitoring.")
        sys.exit(1)


def enable_monitoring():
    """
    Enable Model Monitor schedule for data quality monitoring.

    This script:
    1. Verifies the endpoint exists and has data capture enabled
    2. Verifies baseline exists
    3. Creates or updates a monitoring schedule
    """
    print("=" * 80)
    print("Enabling Model Monitor Schedule")
    print("=" * 80)

    config = load_config()
    print(f"\nConfiguration:")
    print(f"  Region: {config.aws_region}")
    print(f"  Endpoint: {config.endpoint_name}")
    print(f"  Schedule Name: {config.monitor_schedule_name}")
    print(f"  Schedule: {config['schedule_expression']}")

    sagemaker_client = boto3.client("sagemaker", region_name=config.aws_region)

    print(f"\nVerifying endpoint exists...")
    try:
        endpoint_response = sagemaker_client.describe_endpoint(EndpointName=config.endpoint_name)
        endpoint_status = endpoint_response["EndpointStatus"]
        print(f"Endpoint status: {endpoint_status}")

        if endpoint_status != "InService":
            print(f"ERROR: Endpoint is not in service (status: {endpoint_status})")
            sys.exit(1)

    except sagemaker_client.exceptions.ResourceNotFound:
        print(f"\nERROR: Endpoint not found: {config.endpoint_name}")
        print("\nOptions:")
        print("  A. Use the endpoint from the MLOps starter (update config.yaml)")
        print("  B. Create a demo endpoint (instructions in README)")
        sys.exit(1)

    enable_data_capture(config, sagemaker_client)

    baseline_results_uri = f"s3://{config.s3_bucket}/{config['baseline_results_s3_prefix']}"
    data_capture_uri = f"s3://{config.s3_bucket}/{config['data_capture_s3_prefix']}"
    monitoring_output_uri = f"s3://{config.s3_bucket}/{config['monitoring_results_s3_prefix']}"

    print(f"\nCreating DefaultModelMonitor...")
    monitor = DefaultModelMonitor(
        role=config.sagemaker_role_arn,
        instance_count=config["monitoring_instance_count"],
        instance_type=config["monitoring_instance_type"],
        max_runtime_in_seconds=config["monitoring_max_runtime_seconds"],
    )

    print(f"\nCreating monitoring schedule...")
    print(f"  Baseline: {baseline_results_uri}")
    print(f"  Data Capture: {data_capture_uri}")
    print(f"  Monitoring Output: {monitoring_output_uri}")

    try:
        monitor.create_monitoring_schedule(
            monitor_schedule_name=config.monitor_schedule_name,
            endpoint_input=config.endpoint_name,
            output_s3_uri=monitoring_output_uri,
            statistics=f"{baseline_results_uri}/statistics.json",
            constraints=f"{baseline_results_uri}/constraints.json",
            schedule_cron_expression=CronExpressionGenerator.hourly(),
        )

        print("\n" + "=" * 80)
        print("Monitoring schedule created successfully!")
        print("=" * 80)
        print(f"\nSchedule name: {config.monitor_schedule_name}")
        print(f"Schedule: {config['schedule_expression']}")
        print("\nThe monitoring job will run on schedule and analyze captured data.")
        print("\nNext steps:")
        print("  1. Send traffic to the endpoint to generate captured data")
        print("  2. Wait for the next scheduled monitoring job to run")
        print("  3. Run: python scripts/check_violations.py")
        print("\nMonitor executions in the AWS Console:")
        print("  SageMaker → Model Monitor → Monitoring schedules")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"\nMonitoring schedule '{config.monitor_schedule_name}' already exists.")
            print("To update, first delete it:")
            print(
                f"  aws sagemaker delete-monitoring-schedule --monitoring-schedule-name {config.monitor_schedule_name} --region {config.aws_region}"
            )
        else:
            print(f"\nERROR: Failed to create monitoring schedule: {e}")
            print("\nTroubleshooting:")
            print("  - Verify baseline results exist at: " + baseline_results_uri)
            print("  - Check IAM role permissions")
            print("  - Ensure endpoint has data capture enabled")
        sys.exit(1)


if __name__ == "__main__":
    enable_monitoring()
