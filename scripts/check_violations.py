#!/usr/bin/env python3
"""Check Model Monitor executions for violations."""

import json
import sys
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config


def check_violations():
    """
    Check monitoring executions for data quality violations.

    This script:
    1. Lists recent monitoring executions
    2. Downloads and displays constraint violations
    3. Shows statistics and drift information
    """
    print("=" * 80)
    print("Checking Model Monitor Violations")
    print("=" * 80)

    config = load_config()
    print(f"\nConfiguration:")
    print(f"  Region: {config.aws_region}")
    print(f"  Schedule Name: {config.monitor_schedule_name}")

    sagemaker_client = boto3.client("sagemaker", region_name=config.aws_region)
    s3_client = boto3.client("s3", region_name=config.aws_region)

    print(f"\nFetching monitoring executions...")
    try:
        response = sagemaker_client.list_monitoring_executions(
            MonitoringScheduleName=config.monitor_schedule_name,
            MaxResults=10,
            SortOrder="Descending",
        )
    except sagemaker_client.exceptions.ResourceNotFound:
        print(f"\nERROR: Monitoring schedule not found: {config.monitor_schedule_name}")
        print("Run: python scripts/enable_monitoring.py")
        sys.exit(1)

    executions = response.get("MonitoringExecutionSummaries", [])

    if not executions:
        print("\nNo monitoring executions found.")
        print("The schedule may not have run yet, or no data has been captured.")
        print("\nTroubleshooting:")
        print("  1. Verify data capture is enabled on the endpoint")
        print("  2. Send test traffic to the endpoint")
        print("  3. Wait for the monitoring schedule to run (check schedule expression)")
        return

    print(f"\nFound {len(executions)} recent executions:\n")
    print(f"{'Status':<20} {'Created Time':<30} {'Execution ARN'}")
    print("-" * 80)

    for execution in executions:
        status = execution["MonitoringExecutionStatus"]
        created_time = execution["CreationTime"].strftime("%Y-%m-%d %H:%M:%S")
        execution_arn = execution["MonitoringExecutionSummary"].split("/")[-1][:40]
        print(f"{status:<20} {created_time:<30} {execution_arn}...")

    latest_execution = executions[0]
    status = latest_execution["MonitoringExecutionStatus"]

    print("\n" + "=" * 80)
    print(f"Latest Execution Status: {status}")
    print("=" * 80)

    if status in ["Pending", "InProgress"]:
        print("\nThe latest execution is still running.")
        print("Check back later to see results.")
        return

    if status == "Failed":
        print("\nThe latest execution failed.")
        print("Check CloudWatch logs for details:")
        print("  /aws/sagemaker/ProcessingJobs")
        return

    if status != "Completed":
        print(f"\nUnexpected status: {status}")
        return

    processing_job_arn = latest_execution.get("ProcessingJobArn")
    if not processing_job_arn:
        print("\nNo processing job ARN found for this execution.")
        return

    job_name = processing_job_arn.split("/")[-1]
    print(f"\nProcessing Job: {job_name}")

    try:
        job_details = sagemaker_client.describe_processing_job(ProcessingJobName=job_name)
        outputs = job_details.get("ProcessingOutputConfig", {}).get("Outputs", [])

        violations_uri = None
        for output in outputs:
            if output["OutputName"] == "constraint_violations":
                violations_uri = output["S3Output"]["S3Uri"]
                break

        if not violations_uri:
            print("\nNo violations output found.")
            return

        violations_s3_path = violations_uri.replace(f"s3://{config.s3_bucket}/", "")
        violations_key = f"{violations_s3_path}/constraint_violations.json"

        print(f"\nDownloading violations from: s3://{config.s3_bucket}/{violations_key}")

        try:
            response = s3_client.get_object(Bucket=config.s3_bucket, Key=violations_key)
            violations_data = json.loads(response["Body"].read())

            violations = violations_data.get("violations", [])

            if not violations:
                print("\n✓ No violations detected!")
                print("The data quality is within acceptable thresholds.")
            else:
                print(f"\n⚠ Found {len(violations)} violation(s):\n")
                for i, violation in enumerate(violations, 1):
                    print(f"Violation {i}:")
                    print(f"  Feature: {violation.get('feature_name', 'N/A')}")
                    print(f"  Constraint: {violation.get('constraint_check_type', 'N/A')}")
                    print(f"  Description: {violation.get('description', 'N/A')}")
                    print()

            print("\nFull violations report:")
            print(json.dumps(violations_data, indent=2))

        except s3_client.exceptions.NoSuchKey:
            print("\nViolations file not found. This may indicate no violations were detected.")

    except Exception as e:
        print(f"\nERROR: Failed to retrieve violation details: {e}")
        print("\nYou can check monitoring results in S3:")
        print(f"  aws s3 ls s3://{config.s3_bucket}/{config['monitoring_results_s3_prefix']}/ --recursive")


if __name__ == "__main__":
    check_violations()
