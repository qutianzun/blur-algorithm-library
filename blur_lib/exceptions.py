"""Custom exceptions for blur library."""


class BlurError(Exception):
    """Base exception for blur library."""

    pass


class InvalidAlgorithmError(BlurError):
    """Raised when an invalid algorithm is specified."""

    pass


class InvalidConfigError(BlurError):
    """Raised when configuration is invalid."""

    pass


class InvalidImageError(BlurError):
    """Raised when image data is invalid."""

    pass
