"""Gaussian blur algorithm implementation."""

from typing import Any, Dict
import numpy as np
from scipy.ndimage import gaussian_filter

from .base import BlurAlgorithm


class GaussianBlur(BlurAlgorithm):
    """Gaussian blur implementation using scipy.

    Parameters:
        kernel_size: Size of the kernel (odd number, default: 5)
        sigma: Standard deviation for Gaussian kernel (default: 1.0)
    """

    def __init__(self, params: Dict[str, Any]):
        """Initialize Gaussian blur.

        Args:
            params: Algorithm parameters
        """
        super().__init__(params)
        self.kernel_size = params.get("kernel_size", 5)
        self.sigma = params.get("sigma", 1.0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur.

        Args:
            image: Input image (uint8)

        Returns:
            Blurred image (uint8)
        """
        self._validate_image(image)

        # Convert to float for processing
        image_float = image.astype(np.float64)

        # Apply Gaussian filter to each channel
        if len(image.shape) == 2:
            # Grayscale
            blurred = gaussian_filter(image_float, sigma=self.sigma)
        else:
            # Multi-channel
            blurred = np.zeros_like(image_float)
            for channel in range(image.shape[2]):
                blurred[:, :, channel] = gaussian_filter(
                    image_float[:, :, channel], sigma=self.sigma
                )

        # Convert back to uint8
        return self._normalize_to_uint8(blurred)
