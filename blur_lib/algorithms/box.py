"""Box blur algorithm implementation."""

from typing import Any, Dict
import numpy as np
from scipy.ndimage import uniform_filter

from .base import BlurAlgorithm


class BoxBlur(BlurAlgorithm):
    """Box blur (moving average filter) implementation.

    Parameters:
        kernel_size: Size of the box kernel (default: 5)
        iterations: Number of times to apply blur (default: 1)
    """

    def __init__(self, params: Dict[str, Any]):
        """Initialize box blur.

        Args:
            params: Algorithm parameters
        """
        super().__init__(params)
        self.kernel_size = params.get("kernel_size", 5)
        self.iterations = params.get("iterations", 1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply box blur.

        Args:
            image: Input image (uint8)

        Returns:
            Blurred image (uint8)
        """
        self._validate_image(image)

        # Convert to float for processing
        blurred = image.astype(np.float64)

        # Apply box filter multiple times
        for _ in range(self.iterations):
            if len(image.shape) == 2:
                # Grayscale
                blurred = uniform_filter(blurred, size=self.kernel_size)
            else:
                # Multi-channel
                result = np.zeros_like(blurred)
                for channel in range(image.shape[2]):
                    result[:, :, channel] = uniform_filter(
                        blurred[:, :, channel], size=self.kernel_size
                    )
                blurred = result

        # Convert back to uint8
        return self._normalize_to_uint8(blurred)
