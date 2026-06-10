"""Base class for blur algorithms."""

from abc import ABC, abstractmethod
from typing import Any, Dict
import numpy as np


class BlurAlgorithm(ABC):
    """Abstract base class for blur algorithms."""

    def __init__(self, params: Dict[str, Any]):
        """Initialize blur algorithm.

        Args:
            params: Algorithm parameters
        """
        self.params = params

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply blur to image.

        Args:
            image: Input image as numpy array (uint8)

        Returns:
            Blurred image as numpy array (uint8)
        """
        pass

    def _validate_image(self, image: np.ndarray) -> None:
        """Validate input image.

        Args:
            image: Image to validate

        Raises:
            ValueError: If image is invalid
        """
        if not isinstance(image, np.ndarray):
            raise ValueError(f"Expected numpy array, got {type(image).__name__}")

        if len(image.shape) not in (2, 3):
            raise ValueError(f"Expected 2D or 3D array, got shape {image.shape}")

        if image.size == 0:
            raise ValueError("Image cannot be empty")

    def _normalize_to_uint8(self, image: np.ndarray) -> np.ndarray:
        """Normalize image to uint8 range.

        Args:
            image: Image array (may be float or other type)

        Returns:
            Image as uint8 array
        """
        if image.dtype == np.uint8:
            return image

        # Clip to [0, 255] range and convert to uint8
        if np.issubdtype(image.dtype, np.floating):
            return np.clip(image, 0, 255).astype(np.uint8)
        else:
            return np.clip(image, 0, 255).astype(np.uint8)
