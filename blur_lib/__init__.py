"""Blur Algorithm Library - A configurable image blur processing library."""

from .core import BlurProcessor
from .io import load_image, save_image
from .config import Config, validate_config
from .exceptions import (
    BlurError,
    InvalidAlgorithmError,
    InvalidConfigError,
    InvalidImageError,
)

__version__ = "1.0.0"
__all__ = [
    "BlurProcessor",
    "load_image",
    "save_image",
    "Config",
    "validate_config",
    "BlurError",
    "InvalidAlgorithmError",
    "InvalidConfigError",
    "InvalidImageError",
]
