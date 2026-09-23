"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        "aws_region": "us-east-1",
        "sagemaker_role_arn": "arn:aws:iam::999999999999:role/test-role",
        "s3_bucket": "test-bucket-999999999999",
        "endpoint_name": "test-endpoint",
        "monitor_schedule_name": "test-monitor-schedule",
        "schedule_expression": "cron(0 * ? * * *)",
        "baseline_job_name": "test-baseline-job",
        "baseline_instance_type": "ml.m5.xlarge",
        "baseline_instance_count": 1,
        "baseline_max_runtime_seconds": 3600,
        "monitoring_instance_type": "ml.m5.xlarge",
        "monitoring_instance_count": 1,
        "monitoring_max_runtime_seconds": 3600,
        "data_capture_percentage": 100,
        "data_capture_s3_prefix": "data-capture",
        "baseline_results_s3_prefix": "baseline-results",
        "monitoring_results_s3_prefix": "monitoring-results",
        "monitoring_reports_s3_prefix": "monitoring-reports",
    }
