"""Image input/output utilities."""

from typing import Union
from pathlib import Path
import numpy as np
from PIL import Image

from .exceptions import InvalidImageError


def load_image(filepath: Union[str, Path]) -> np.ndarray:
    """Load image from file.

    Args:
        filepath: Path to image file

    Returns:
        Image as numpy array (uint8, RGB or RGBA)

    Raises:
        InvalidImageError: If image cannot be loaded
    """
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            raise InvalidImageError(f"Image file not found: {filepath}")

        image = Image.open(filepath)
        # Convert to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGBA")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        return np.array(image, dtype=np.uint8)
    except InvalidImageError:
        raise
    except Exception as e:
        raise InvalidImageError(f"Failed to load image: {str(e)}")


def save_image(image: np.ndarray, filepath: Union[str, Path]) -> None:
    """Save image to file.

    Args:
        image: Image as numpy array
        filepath: Path to save image

    Raises:
        InvalidImageError: If image cannot be saved
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Ensure image is uint8
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        # Convert numpy array to PIL Image
        if len(image.shape) == 2:
            # Grayscale
            pil_image = Image.fromarray(image, mode="L")
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                pil_image = Image.fromarray(image, mode="RGB")
            elif image.shape[2] == 4:
                pil_image = Image.fromarray(image, mode="RGBA")
            else:
                raise InvalidImageError(
                    f"Unsupported image shape: {image.shape}. Expected (H, W) or (H, W, 3/4)"
                )
        else:
            raise InvalidImageError(
                f"Unsupported image shape: {image.shape}. Expected (H, W) or (H, W, 3/4)"
            )

        pil_image.save(filepath)
    except InvalidImageError:
        raise
    except Exception as e:
        raise InvalidImageError(f"Failed to save image: {str(e)}")


def validate_image(image: np.ndarray) -> bool:
    """Validate image array.

    Args:
        image: Image as numpy array

    Returns:
        True if valid

    Raises:
        InvalidImageError: If image is invalid
    """
    if not isinstance(image, np.ndarray):
        raise InvalidImageError(
            f"Image must be numpy array, got {type(image).__name__}"
        )

    if len(image.shape) not in (2, 3):
        raise InvalidImageError(
            f"Image must be 2D or 3D array, got shape {image.shape}"
        )

    if len(image.shape) == 3:
        if image.shape[2] not in (3, 4):
            raise InvalidImageError(
                f"Image must have 3 or 4 channels, got {image.shape[2]}"
            )

    if not np.issubdtype(image.dtype, np.integer):
        raise InvalidImageError(f"Image dtype must be integer, got {image.dtype}")

    return True
