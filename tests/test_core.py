"""Tests for core blur processor."""

import pytest
import numpy as np
from blur_lib.core import BlurProcessor
from blur_lib.config import Config
from blur_lib.exceptions import InvalidImageError, InvalidAlgorithmError


class TestBlurProcessor:
    """Test BlurProcessor class."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        return np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    @pytest.fixture
    def grayscale_image(self):
        """Create a grayscale sample image."""
        return np.random.randint(0, 255, (128, 128), dtype=np.uint8)

    def test_init_with_dict_config(self):
        """Test initializing processor with dict config."""
        config = {"algorithm": "gaussian", "params": {"sigma": 1.5}}
        processor = BlurProcessor(config)
        assert processor.config.algorithm == "gaussian"

    def test_init_with_config_object(self):
        """Test initializing processor with Config object."""
        config = Config("box", {"kernel_size": 5})
        processor = BlurProcessor(config)
        assert processor.config.algorithm == "box"

    def test_invalid_algorithm_raises_error(self):
        """Test invalid algorithm raises error."""
        config = {"algorithm": "invalid_blur"}
        with pytest.raises((InvalidAlgorithmError, Exception)):
            BlurProcessor(config)

    def test_gaussian_blur_output_shape(self, sample_image):
        """Test Gaussian blur output shape matches input."""
        config = {"algorithm": "gaussian", "params": {"sigma": 1.5}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_box_blur_output_shape(self, sample_image):
        """Test Box blur output shape matches input."""
        config = {"algorithm": "box", "params": {"kernel_size": 5}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_kawase_blur_output_shape(self, sample_image):
        """Test Kawase blur output shape matches input."""
        config = {"algorithm": "kawase", "params": {"iterations": 2}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_dual_blur_output_shape(self, sample_image):
        """Test Dual blur output shape matches input."""
        config = {"algorithm": "dual", "params": {"iterations": 2}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_output_dtype_is_uint8(self, sample_image):
        """Test output dtype is uint8."""
        config = {"algorithm": "gaussian", "params": {"sigma": 1.0}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert result.dtype == np.uint8

    def test_grayscale_image(self, grayscale_image):
        """Test processing grayscale image."""
        config = {"algorithm": "gaussian", "params": {"sigma": 1.0}}
        processor = BlurProcessor(config)
        result = processor.apply(grayscale_image)
        assert result.shape == grayscale_image.shape
        assert result.dtype == np.uint8

    def test_invalid_image_type_raises_error(self):
        """Test invalid image type raises error."""
        config = {"algorithm": "gaussian"}
        processor = BlurProcessor(config)
        with pytest.raises(InvalidImageError):
            processor.apply([1, 2, 3])

    def test_change_algorithm(self, sample_image):
        """Test changing algorithm dynamically."""
        processor = BlurProcessor({"algorithm": "gaussian"})
        result1 = processor.apply(sample_image.copy())

        processor.change_algorithm({"algorithm": "box", "params": {"kernel_size": 5}})
        result2 = processor.apply(sample_image.copy())

        assert processor.config.algorithm == "box"

    def test_get_config(self):
        """Test getting current config."""
        config = {"algorithm": "box", "params": {"kernel_size": 7}}
        processor = BlurProcessor(config)
        retrieved_config = processor.get_config()
        assert retrieved_config.algorithm == "box"

    def test_blur_reduces_variance(self, sample_image):
        """Test that blur reduces image variance."""
        config = {"algorithm": "gaussian", "params": {"sigma": 3.0}}
        processor = BlurProcessor(config)
        result = processor.apply(sample_image)
        assert np.var(result) < np.var(sample_image)
