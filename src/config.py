"""Configuration management utilities."""

from pathlib import Path
from typing import Any, Dict

import yaml


class Config:
    """Configuration manager for SageMaker Model Monitor."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                "Copy config/config.example.yaml to config/config.yaml and update with your values."
            )

        with open(self.config_path) as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)

        self._validate()

    def _validate(self):
        """Validate critical configuration values."""
        required_fields = [
            "aws_region",
            "sagemaker_role_arn",
            "s3_bucket",
            "endpoint_name",
            "monitor_schedule_name",
        ]

        for field in required_fields:
            if field not in self._config:
                raise ValueError(f"Missing required config field: {field}")

        role_arn = self._config["sagemaker_role_arn"]
        if "123456789012" in role_arn:
            raise ValueError(
                "Please update the SageMaker role ARN in config.yaml with your actual AWS account ID.\n"
                "Run 'terraform output' in the infra/ directory to get the correct ARN."
            )

        bucket = self._config["s3_bucket"]
        if "123456789012" in bucket:
            raise ValueError(
                "Please update the S3 bucket name in config.yaml with your actual AWS account ID.\n"
                "Run 'terraform output' in the infra/ directory to get the correct bucket name."
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        return key in self._config

    @property
    def aws_region(self) -> str:
        return self._config["aws_region"]

    @property
    def sagemaker_role_arn(self) -> str:
        return self._config["sagemaker_role_arn"]

    @property
    def s3_bucket(self) -> str:
        return self._config["s3_bucket"]

    @property
    def endpoint_name(self) -> str:
        return self._config["endpoint_name"]

    @property
    def monitor_schedule_name(self) -> str:
        return self._config["monitor_schedule_name"]


def load_config(config_path: str = "config/config.yaml") -> Config:
    """
    Load configuration from file.

    Args:
        config_path: Path to configuration file

    Returns:
        Config object
    """
    return Config(config_path)
