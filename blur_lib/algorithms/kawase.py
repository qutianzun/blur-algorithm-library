"""Kawase blur algorithm implementation."""

from typing import Any, Dict
import numpy as np
from scipy.ndimage import shift

from .base import BlurAlgorithm


class KawaseBlur(BlurAlgorithm):
    """Kawase blur implementation.

    Kawase blur is a fast approximation of Gaussian blur using
    multiple shifted box blur operations.

    Parameters:
        iterations: Number of blur iterations (default: 4)
        offset: Pixel offset for each iteration (default: 1)
    """

    def __init__(self, params: Dict[str, Any]):
        """Initialize Kawase blur.

        Args:
            params: Algorithm parameters
        """
        super().__init__(params)
        self.iterations = params.get("iterations", 4)
        self.offset = params.get("offset", 1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply Kawase blur.

        Args:
            image: Input image (uint8)

        Returns:
            Blurred image (uint8)
        """
        self._validate_image(image)

        # Convert to float for processing
        result = image.astype(np.float64)

        # Apply Kawase blur
        for iteration in range(self.iterations):
            # Current offset for this iteration
            current_offset = self.offset * (2 ** iteration)

            # Create shifted versions
            if len(image.shape) == 2:
                # Grayscale
                shifted_sum = result.copy()
                shifted_sum += shift(result, (current_offset, 0), cval=0)
                shifted_sum += shift(result, (-current_offset, 0), cval=0)
                shifted_sum += shift(result, (0, current_offset), cval=0)
                shifted_sum += shift(result, (0, -current_offset), cval=0)
                result = shifted_sum / 5.0
            else:
                # Multi-channel
                shifted_sum = result.copy()
                shifted_sum += shift(result, (current_offset, 0, 0), cval=0)
                shifted_sum += shift(result, (-current_offset, 0, 0), cval=0)
                shifted_sum += shift(result, (0, current_offset, 0), cval=0)
                shifted_sum += shift(result, (0, -current_offset, 0), cval=0)
                result = shifted_sum / 5.0

        # Convert back to uint8
        return self._normalize_to_uint8(result)
