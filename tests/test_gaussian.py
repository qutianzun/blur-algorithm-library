"""Tests for Gaussian blur algorithm."""

import pytest
import numpy as np
from blur_lib.algorithms.gaussian import GaussianBlur


class TestGaussianBlur:
    """Test GaussianBlur class."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image."""
        return np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    @pytest.fixture
    def gaussian_blur(self):
        """Create GaussianBlur instance."""
        return GaussianBlur({"kernel_size": 5, "sigma": 1.0})

    def test_apply_returns_uint8(self, gaussian_blur, sample_image):
        """Test that output is uint8."""
        result = gaussian_blur.apply(sample_image)
        assert result.dtype == np.uint8

    def test_apply_preserves_shape(self, gaussian_blur, sample_image):
        """Test that output shape matches input."""
        result = gaussian_blur.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_apply_with_different_sigma(self, sample_image):
        """Test with different sigma values."""
        blur1 = GaussianBlur({"sigma": 1.0})
        blur2 = GaussianBlur({"sigma": 3.0})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert np.var(result2) < np.var(result1)

    def test_apply_grayscale(self):
        """Test with grayscale image."""
        image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        blur = GaussianBlur({"sigma": 1.5})
        result = blur.apply(image)
        assert result.shape == image.shape

    def test_apply_with_zero_image(self):
        """Test with all-zero image."""
        image = np.zeros((64, 64, 3), dtype=np.uint8)
        blur = GaussianBlur({"sigma": 1.0})
        result = blur.apply(image)
        assert np.all(result == 0)

    def test_apply_with_constant_image(self):
        """Test with constant-value image."""
        image = np.full((64, 64, 3), 128, dtype=np.uint8)
        blur = GaussianBlur({"sigma": 2.0})
        result = blur.apply(image)
        assert np.allclose(result, 128, atol=5)
