"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.config import Config


def test_config_missing_file():
    """Test error handling when config file is missing."""
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        Config("nonexistent.yaml")


def test_config_loads_valid_file(sample_config_dict):
    """Test loading a valid configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config_dict, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.aws_region == "us-east-1"
        assert config.sagemaker_role_arn == "arn:aws:iam::999999999999:role/test-role"
        assert config.s3_bucket == "test-bucket-999999999999"
        assert config.endpoint_name == "test-endpoint"
    finally:
        Path(temp_path).unlink()


def test_config_validates_placeholder_role():
    """Test validation rejects placeholder account IDs in role ARN."""
    invalid_config = {
        "aws_region": "us-east-1",
        "sagemaker_role_arn": "arn:aws:iam::123456789012:role/test-role",
        "s3_bucket": "test-bucket",
        "endpoint_name": "test-endpoint",
        "monitor_schedule_name": "test-schedule",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(invalid_config, f)
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="actual AWS account ID"):
            Config(temp_path)
    finally:
        Path(temp_path).unlink()


def test_config_validates_placeholder_bucket():
    """Test validation rejects placeholder account IDs in bucket name."""
    invalid_config = {
        "aws_region": "us-east-1",
        "sagemaker_role_arn": "arn:aws:iam::999999999999:role/test-role",
        "s3_bucket": "test-bucket-123456789012",
        "endpoint_name": "test-endpoint",
        "monitor_schedule_name": "test-schedule",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(invalid_config, f)
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="actual AWS account ID"):
            Config(temp_path)
    finally:
        Path(temp_path).unlink()


def test_config_validates_required_fields():
    """Test validation rejects missing required fields."""
    invalid_config = {
        "aws_region": "us-east-1",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(invalid_config, f)
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="Missing required config field"):
            Config(temp_path)
    finally:
        Path(temp_path).unlink()


def test_config_get_method(sample_config_dict):
    """Test the get method with default values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config_dict, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.get("aws_region") == "us-east-1"
        assert config.get("nonexistent_key", "default") == "default"
        assert config.get("nonexistent_key") is None
    finally:
        Path(temp_path).unlink()


def test_config_bracket_notation(sample_config_dict):
    """Test accessing config values with bracket notation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_config_dict, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config["aws_region"] == "us-east-1"
        assert "aws_region" in config
        assert "nonexistent" not in config
    finally:
        Path(temp_path).unlink()
