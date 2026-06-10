"""Configuration management for blur algorithms."""

from typing import Any, Dict, Optional
import json
import yaml

from .exceptions import InvalidConfigError


class Config:
    """Configuration class for blur processing."""

    SUPPORTED_ALGORITHMS = {"gaussian", "box", "kawase", "dual"}

    ALGORITHM_DEFAULTS: Dict[str, Dict[str, Any]] = {
        "gaussian": {"kernel_size": 5, "sigma": 1.0},
        "box": {"kernel_size": 5, "iterations": 1},
        "kawase": {"iterations": 4, "offset": 1},
        "dual": {"iterations": 4, "downsample_factor": 2, "upsample_filter": "linear"},
    }

    ALGORITHM_CONSTRAINTS: Dict[str, Dict[str, Any]] = {
        "gaussian": {
            "kernel_size": {"type": int, "min": 1, "max": 255},
            "sigma": {"type": float, "min": 0.1, "max": 100.0},
        },
        "box": {
            "kernel_size": {"type": int, "min": 1, "max": 255},
            "iterations": {"type": int, "min": 1, "max": 10},
        },
        "kawase": {
            "iterations": {"type": int, "min": 1, "max": 20},
            "offset": {"type": int, "min": 1, "max": 10},
        },
        "dual": {
            "iterations": {"type": int, "min": 1, "max": 20},
            "downsample_factor": {"type": int, "min": 1, "max": 8},
            "upsample_filter": {"type": str, "values": ["linear", "nearest"]},
        },
    }

    def __init__(
        self,
        algorithm: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """Initialize configuration.

        Args:
            algorithm: Name of blur algorithm
            params: Algorithm-specific parameters

        Raises:
            InvalidConfigError: If configuration is invalid
        """
        self.algorithm = algorithm.lower()
        self.params = params or {}

        self._validate()
        self._apply_defaults()

    def _validate(self) -> None:
        """Validate configuration.

        Raises:
            InvalidConfigError: If validation fails
        """
        if self.algorithm not in self.SUPPORTED_ALGORITHMS:
            raise InvalidConfigError(
                f"Unsupported algorithm: {self.algorithm}. "
                f"Supported: {self.SUPPORTED_ALGORITHMS}"
            )

        constraints = self.ALGORITHM_CONSTRAINTS.get(self.algorithm, {})
        for param_name, param_value in self.params.items():
            if param_name not in constraints:
                raise InvalidConfigError(
                    f"Unknown parameter '{param_name}' for algorithm '{self.algorithm}'"
                )

            constraint = constraints[param_name]
            expected_type = constraint.get("type")

            if not isinstance(param_value, expected_type):
                raise InvalidConfigError(
                    f"Parameter '{param_name}' must be {expected_type.__name__}, "
                    f"got {type(param_value).__name__}"
                )

            if "min" in constraint and param_value < constraint["min"]:
                raise InvalidConfigError(
                    f"Parameter '{param_name}' must be >= {constraint['min']}, got {param_value}"
                )

            if "max" in constraint and param_value > constraint["max"]:
                raise InvalidConfigError(
                    f"Parameter '{param_name}' must be <= {constraint['max']}, got {param_value}"
                )

            if "values" in constraint and param_value not in constraint["values"]:
                raise InvalidConfigError(
                    f"Parameter '{param_name}' must be one of {constraint['values']}, "
                    f"got {param_value}"
                )

    def _apply_defaults(self) -> None:
        """Apply default parameters for algorithm."""
        defaults = self.ALGORITHM_DEFAULTS.get(self.algorithm, {})
        for key, value in defaults.items():
            if key not in self.params:
                self.params[key] = value

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create config from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Config instance

        Raises:
            InvalidConfigError: If dictionary format is invalid
        """
        if "algorithm" not in config_dict:
            raise InvalidConfigError("'algorithm' key is required in config")

        algorithm = config_dict["algorithm"]
        params = config_dict.get("params", {})

        return cls(algorithm, params)

    @classmethod
    def from_json(cls, json_str: str) -> "Config":
        """Create config from JSON string.

        Args:
            json_str: JSON configuration string

        Returns:
            Config instance
        """
        config_dict = json.loads(json_str)
        return cls.from_dict(config_dict)

    @classmethod
    def from_json_file(cls, filepath: str) -> "Config":
        """Create config from JSON file.

        Args:
            filepath: Path to JSON configuration file

        Returns:
            Config instance
        """
        with open(filepath, "r") as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Config":
        """Create config from YAML string.

        Args:
            yaml_str: YAML configuration string

        Returns:
            Config instance
        """
        config_dict = yaml.safe_load(yaml_str)
        return cls.from_dict(config_dict)

    @classmethod
    def from_yaml_file(cls, filepath: str) -> "Config":
        """Create config from YAML file.

        Args:
            filepath: Path to YAML configuration file

        Returns:
            Config instance
        """
        with open(filepath, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Configuration dictionary
        """
        return {"algorithm": self.algorithm, "params": self.params}

    def to_json(self) -> str:
        """Convert config to JSON string.

        Returns:
            JSON configuration string
        """
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self) -> str:
        """String representation."""
        return f"Config(algorithm='{self.algorithm}', params={self.params})"


def validate_config(config_dict: Dict[str, Any]) -> bool:
    """Validate configuration dictionary.

    Args:
        config_dict: Configuration dictionary to validate

    Returns:
        True if valid

    Raises:
        InvalidConfigError: If configuration is invalid
    """
    try:
        Config.from_dict(config_dict)
        return True
    except InvalidConfigError:
        raise
