"""Tests for Kawase blur algorithm."""

import pytest
import numpy as np
from blur_lib.algorithms.kawase import KawaseBlur


class TestKawaseBlur:
    """Test KawaseBlur class."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image."""
        return np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    @pytest.fixture
    def kawase_blur(self):
        """Create KawaseBlur instance."""
        return KawaseBlur({"iterations": 4, "offset": 1})

    def test_apply_returns_uint8(self, kawase_blur, sample_image):
        """Test that output is uint8."""
        result = kawase_blur.apply(sample_image)
        assert result.dtype == np.uint8

    def test_apply_preserves_shape(self, kawase_blur, sample_image):
        """Test that output shape matches input."""
        result = kawase_blur.apply(sample_image)
        assert result.shape == sample_image.shape

    def test_apply_with_different_iterations(self, sample_image):
        """Test with different iteration counts."""
        blur1 = KawaseBlur({"iterations": 1})
        blur2 = KawaseBlur({"iterations": 5})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert np.var(result2) < np.var(result1)

    def test_apply_with_different_offset(self, sample_image):
        """Test with different offset values."""
        blur1 = KawaseBlur({"iterations": 3, "offset": 1})
        blur2 = KawaseBlur({"iterations": 3, "offset": 2})

        result1 = blur1.apply(sample_image.copy())
        result2 = blur2.apply(sample_image.copy())

        assert not np.array_equal(result1, result2)

    def test_apply_grayscale(self):
        """Test with grayscale image."""
        image = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        blur = KawaseBlur({"iterations": 3})
        result = blur.apply(image)
        assert result.shape == image.shape
