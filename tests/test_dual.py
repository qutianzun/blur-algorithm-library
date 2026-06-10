"""Tests for Dual blur algorithm."""

import pytest
import numpy as np
from blur_lib.algorithms.dual import DualBlur


class TestDualBlur:
    """Test DualBlur class."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image."""
        return np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    @pytest.fixture
    def dual_blur(self):
        """Create DualBlur instance."""
        return DualBlur({"iterations": 2, "downsample_factor": 2})

    def test_apply_returns_uint8(self, dual_blur, sample_image):
        """Test that output is uint8."""
        result = dual_blur.apply(sample_image)
        assert result.dtype == np.uint8

    def test_apply_preserves_shape(self, dual_blur, sample_image):
        """Test that output shape matches input."""
        result = dual_blur.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_apply_with_different_iterations(self, sample_image):
        """Test with different iteration counts."""
        blur1 = DualBlur({"iterations": 1})
        blur2 = DualBlur({"iterations": 4})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert np.var(result2) < np.var(result1)

    def test_apply_with_different_downsample_factor(self, sample_image):
        """Test with different downsample factors."""
        blur1 = DualBlur({"iterations": 2, "downsample_factor": 2})
        blur2 = DualBlur({"iterations": 2, "downsample_factor": 4})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert not np.array_equal(result1, result2)

    def test_apply_grayscale(self):
        """Test with grayscale image."""
        image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        blur = DualBlur({"iterations": 2})
        result = blur.apply(image)
        assert result.shape == image.shape

    def test_apply_with_linear_upsampling(self, sample_image):
        """Test with linear upsampling filter."""
        blur = DualBlur(
            {"iterations": 2, "downsample_factor": 2, "upsample_filter": "linear"}
        )
        result = blur.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_apply_with_nearest_upsampling(self, sample_image):
        """Test with nearest upsampling filter."""
        blur = DualBlur(
            {"iterations": 2, "downsample_factor": 2, "upsample_filter": "nearest"}
        )
        result = blur.apply(sample_image)
        assert result.shape == sample_image.shape
