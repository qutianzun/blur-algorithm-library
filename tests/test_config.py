"""Tests for configuration module."""

import pytest
import json
from blur_lib.config import Config, validate_config
from blur_lib.exceptions import InvalidConfigError


class TestConfig:
    """Test Config class."""

    def test_valid_gaussian_config(self):
        """Test creating valid Gaussian config."""
        config = Config("gaussian", {"kernel_size": 5, "sigma": 1.0})
        assert config.algorithm == "gaussian"
        assert config.params["kernel_size"] == 5
        assert config.params["sigma"] == 1.0

    def test_valid_box_config(self):
        """Test creating valid Box config."""
        config = Config("box", {"kernel_size": 5, "iterations": 2})
        assert config.algorithm == "box"
        assert config.params["kernel_size"] == 5
        assert config.params["iterations"] == 2

    def test_valid_kawase_config(self):
        """Test creating valid Kawase config."""
        config = Config("kawase", {"iterations": 4, "offset": 1})
        assert config.algorithm == "kawase"
        assert config.params["iterations"] == 4

    def test_valid_dual_config(self):
        """Test creating valid Dual config."""
        config = Config("dual", {"iterations": 4, "downsample_factor": 2})
        assert config.algorithm == "dual"

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises error."""
        with pytest.raises(InvalidConfigError):
            Config("invalid_algo", {})

    def test_invalid_parameter_type(self):
        """Test invalid parameter type raises error."""
        with pytest.raises(InvalidConfigError):
            Config("gaussian", {"kernel_size": "5"})

    def test_parameter_too_small(self):
        """Test parameter below minimum raises error."""
        with pytest.raises(InvalidConfigError):
            Config("gaussian", {"kernel_size": 0})

    def test_parameter_too_large(self):
        """Test parameter above maximum raises error."""
        with pytest.raises(InvalidConfigError):
            Config("gaussian", {"kernel_size": 300})

    def test_unknown_parameter(self):
        """Test unknown parameter raises error."""
        with pytest.raises(InvalidConfigError):
            Config("gaussian", {"invalid_param": 5})

    def test_defaults_applied(self):
        """Test default parameters are applied."""
        config = Config("gaussian", {})
        assert config.params["kernel_size"] == 5
        assert config.params["sigma"] == 1.0

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {"algorithm": "box", "params": {"kernel_size": 7}}
        config = Config.from_dict(config_dict)
        assert config.algorithm == "box"
        assert config.params["kernel_size"] == 7

    def test_from_json(self):
        """Test creating config from JSON."""
        json_str = '{"algorithm": "gaussian", "params": {"sigma": 2.0}}'
        config = Config.from_json(json_str)
        assert config.algorithm == "gaussian"
        assert config.params["sigma"] == 2.0

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config("box", {"kernel_size": 7})
        config_dict = config.to_dict()
        assert config_dict["algorithm"] == "box"
        assert "kernel_size" in config_dict["params"]

    def test_to_json(self):
        """Test converting config to JSON."""
        config = Config("gaussian", {"sigma": 2.0})
        json_str = config.to_json()
        config_dict = json.loads(json_str)
        assert config_dict["algorithm"] == "gaussian"

    def test_validate_config_valid(self):
        """Test validate_config with valid config."""
        config_dict = {"algorithm": "box", "params": {"kernel_size": 5}}
        assert validate_config(config_dict) is True

    def test_validate_config_invalid(self):
        """Test validate_config with invalid config."""
        config_dict = {"algorithm": "invalid"}
        with pytest.raises(InvalidConfigError):
            validate_config(config_dict)

    def test_case_insensitive_algorithm(self):
        """Test algorithm names are case-insensitive."""
        config = Config("GAUSSIAN", {})
        assert config.algorithm == "gaussian"
