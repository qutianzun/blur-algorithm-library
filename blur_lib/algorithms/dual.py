"""Dual blur algorithm implementation."""

from typing import Any, Dict
import numpy as np
from scipy.ndimage import zoom, uniform_filter

from .base import BlurAlgorithm


class DualBlur(BlurAlgorithm):
    """Dual blur implementation using downsampling and upsampling.

    Dual blur applies blur at multiple scales for fast approximation.

    Parameters:
        iterations: Number of blur iterations (default: 4)
        downsample_factor: Factor for downsampling (default: 2)
        upsample_filter: Interpolation method 'linear' or 'nearest' (default: 'linear')
    """

    def __init__(self, params: Dict[str, Any]):
        """Initialize dual blur.

        Args:
            params: Algorithm parameters
        """
        super().__init__(params)
        self.iterations = params.get("iterations", 4)
        self.downsample_factor = params.get("downsample_factor", 2)
        self.upsample_filter = params.get("upsample_filter", "linear")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply dual blur.

        Args:
            image: Input image (uint8)

        Returns:
            Blurred image (uint8)
        """
        self._validate_image(image)

        # Convert to float for processing
        result = image.astype(np.float64)

        is_grayscale = len(image.shape) == 2

        # Apply dual blur iterations
        for _ in range(self.iterations):
            if is_grayscale:
                # Downsampling
                zoom_factor = 1.0 / self.downsample_factor
                downsampled = zoom(result, zoom_factor, order=1)

                # Blur at lower resolution
                blurred_down = uniform_filter(downsampled, size=3)

                # Upsampling
                upsampled = zoom(blurred_down, self.downsample_factor, order=1)

                # Ensure same size as original
                h, w = result.shape
                upsampled = upsampled[:h, :w]

                # Blend with original
                result = (result + upsampled) / 2.0
            else:
                # Multi-channel
                h, w, c = result.shape
                zoom_factor = 1.0 / self.downsample_factor

                # Process each channel
                blurred = np.zeros_like(result)
                for channel in range(c):
                    channel_data = result[:, :, channel]

                    # Downsampling
                    downsampled = zoom(channel_data, zoom_factor, order=1)

                    # Blur at lower resolution
                    blurred_down = uniform_filter(downsampled, size=3)

                    # Upsampling
                    upsampled = zoom(blurred_down, self.downsample_factor, order=1)

                    # Ensure same size as original
                    upsampled = upsampled[:h, :w]

                    # Blend with original
                    blurred[:, :, channel] = (channel_data + upsampled) / 2.0

                result = blurred

        # Convert back to uint8
        return self._normalize_to_uint8(result)
