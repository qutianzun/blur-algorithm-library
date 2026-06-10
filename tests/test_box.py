"""Tests for Box blur algorithm."""

import pytest
import numpy as np
from blur_lib.algorithms.box import BoxBlur


class TestBoxBlur:
    """Test BoxBlur class."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image."""
        return np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    @pytest.fixture
    def box_blur(self):
        """Create BoxBlur instance."""
        return BoxBlur({"kernel_size": 5, "iterations": 1})

    def test_apply_returns_uint8(self, box_blur, sample_image):
        """Test that output is uint8."""
        result = box_blur.apply(sample_image)
        assert result.dtype == np.uint8

    def test_apply_preserves_shape(self, box_blur, sample_image):
        """Test that output shape matches input."""
        result = box_blur.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_apply_with_different_kernel_sizes(self, sample_image):
        """Test with different kernel sizes."""
        blur1 = BoxBlur({"kernel_size": 3})
        blur2 = BoxBlur({"kernel_size": 7})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert np.var(result2) < np.var(result1)

    def test_apply_with_multiple_iterations(self, sample_image):
        """Test with multiple iterations."""
        blur1 = BoxBlur({"kernel_size": 5, "iterations": 1})
        blur2 = BoxBlur({"kernel_size": 5, "iterations": 3})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert np.var(result2) < np.var(result1)

    def test_apply_grayscale(self):
        """Test with grayscale image."""
        image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        blur = BoxBlur({"kernel_size": 5})
        result = blur.apply(image)
        assert result.shape == image.shape

    def test_apply_with_small_image(self):
        """Test with small image."""
        image = np.random.randint(0, 255, (8, 8, 3), dtype=np.uint8)
        blur = BoxBlur({"kernel_size": 3})
        result = blur.apply(image)
        assert result.shape == image.shape
