# Blur Algorithm Library

A configurable, modular Python image blur processing library supporting multiple blur algorithms with unified interface.

## Features

- **Multiple Blur Algorithms**: Gaussian, Box, Kawase, and Dual blur
- **Unified Interface**: Consistent API across all algorithms
- **Configuration-Driven**: Easy algorithm selection and parameter management
- **Type Annotations**: Full type hints for better IDE support
- **Comprehensive Tests**: 100% test coverage with pytest
- **Performance Benchmarks**: Built-in performance testing
- **Easy to Extend**: Clear base class for adding new algorithms

## Installation

### Requirements

- Python 3.9+
- NumPy >= 1.21.0
- Pillow >= 9.0.0
- SciPy >= 1.7.0
- PyYAML >= 6.0

### From Source

```bash
# Clone repository
git clone https://github.com/qutianzun/blur-algorithm-library.git
cd blur-algorithm-library

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from blur_lib import BlurProcessor, load_image, save_image
import numpy as np

# Create or load an image
image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

# Define blur configuration
config = {
    "algorithm": "gaussian",
    "params": {
        "kernel_size": 5,
        "sigma": 1.5
    }
}

# Create processor and apply blur
processor = BlurProcessor(config)
result = processor.apply(image)

# Save result
save_image(result, "output.png")
```

### Different Algorithms

#### Gaussian Blur

```python
config = {
    "algorithm": "gaussian",
    "params": {
        "kernel_size": 5,
        "sigma": 1.5
    }
}
processor = BlurProcessor(config)
result = processor.apply(image)
```

#### Box Blur

```python
config = {
    "algorithm": "box",
    "params": {
        "kernel_size": 5,
        "iterations": 2
    }
}
processor = BlurProcessor(config)
result = processor.apply(image)
```

#### Kawase Blur

```python
config = {
    "algorithm": "kawase",
    "params": {
        "iterations": 4,
        "offset": 1
    }
}
processor = BlurProcessor(config)
result = processor.apply(image)
```

#### Dual Blur

```python
config = {
    "algorithm": "dual",
    "params": {
        "iterations": 4,
        "downsample_factor": 2,
        "upsample_filter": "linear"
    }
}
processor = BlurProcessor(config)
result = processor.apply(image)
```

### Configuration Management

#### From Dictionary

```python
from blur_lib import Config

config = Config("gaussian", {"sigma": 2.0})
processor = BlurProcessor(config)
```

#### From JSON String

```python
json_str = '{"algorithm": "box", "params": {"kernel_size": 7}}'
config = Config.from_json(json_str)
processor = BlurProcessor(config)
```

#### From JSON File

```python
config = Config.from_json_file("config.json")
processor = BlurProcessor(config)
```

#### From YAML File

```python
config = Config.from_yaml_file("config.yaml")
processor = BlurProcessor(config)
```

#### Export Configuration

```python
config = Config("gaussian", {"sigma": 1.5})
json_str = config.to_json()
config_dict = config.to_dict()
```

### Batch Processing

```python
config = {"algorithm": "gaussian", "params": {"sigma": 1.5}}
processor = BlurProcessor(config)

# Process multiple images
for i in range(10):
    image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    result = processor.apply(image)
    save_image(result, f"output_{i}.png")
```

### Dynamic Algorithm Switching

```python
processor = BlurProcessor({"algorithm": "gaussian", "params": {"sigma": 1.0}})
result1 = processor.apply(image)

# Switch algorithm
processor.change_algorithm({"algorithm": "box", "params": {"kernel_size": 5}})
result2 = processor.apply(image)
```

## Algorithm Details

### Gaussian Blur

Classic Gaussian blur using SciPy's `gaussian_filter`. Provides smooth blur with control over sigma (standard deviation).

**Parameters:**
- `kernel_size`: Reference kernel size (int, 1-255, default: 5)
- `sigma`: Standard deviation (float, 0.1-100.0, default: 1.0)

**Use Case:** Best for smooth, natural-looking blur

### Box Blur

Simple moving average filter. Can be applied multiple times for stronger blur effect.

**Parameters:**
- `kernel_size`: Size of box kernel (int, 1-255, default: 5)
- `iterations`: Number of blur iterations (int, 1-10, default: 1)

**Use Case:** Fast blur, useful for real-time applications

### Kawase Blur

Fast approximation of Gaussian blur using multiple shifted box blur operations. Efficient for large blur radii.

**Parameters:**
- `iterations`: Number of iterations (int, 1-20, default: 4)
- `offset`: Pixel offset per iteration (int, 1-10, default: 1)

**Use Case:** Fast blur for performance-critical applications

### Dual Blur

Multi-scale blur using downsampling and upsampling. Combines blur at different resolutions.

**Parameters:**
- `iterations`: Number of iterations (int, 1-20, default: 4)
- `downsample_factor`: Downsampling factor (int, 1-8, default: 2)
- `upsample_filter`: Interpolation method: 'linear' or 'nearest' (str, default: 'linear')

**Use Case:** Efficient large blur effects, good for artistic effects

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_gaussian.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=blur_lib --cov-report=html
```

### Run Tests with Specific Markers

```bash
pytest tests/ -v -m "not slow"
```

## Performance Benchmarking

### Run Benchmark Suite

```bash
python benchmarks/benchmark_blur.py
```

### Benchmark Output

```
================================================================================
Blur Algorithm Performance Benchmark
================================================================================

Image Size: 256x256
--------------------------------------------------------------------------------
  Algorithm: GAUSSIAN
    Average Time: 1.23 ms
    Min Time:     1.15 ms
    Max Time:     1.45 ms
    FPS:          813.0

  Algorithm: BOX
    Average Time: 0.87 ms
    Min Time:     0.82 ms
    Max Time:     0.95 ms
    FPS:          1149.4
    
  ...
```

## Configuration File Examples

### JSON Configuration

```json
{
  "algorithm": "gaussian",
  "params": {
    "kernel_size": 5,
    "sigma": 1.5
  }
}
```

### YAML Configuration

```yaml
algorithm: box
params:
  kernel_size: 7
  iterations: 2
```

## Project Structure

```
blur-algorithm-library/
├── blur_lib/                 # Main package
│   ├── __init__.py
│   ├── core.py              # Core processor
│   ├── config.py            # Configuration management
│   ├── io.py                # Image I/O utilities
│   ├── exceptions.py        # Custom exceptions
│   └── algorithms/          # Algorithm implementations
│       ├── __init__.py
│       ├── base.py          # Base algorithm class
│       ├── gaussian.py      # Gaussian blur
│       ├── box.py           # Box blur
│       ├── kawase.py        # Kawase blur
│       └── dual.py          # Dual blur
├── tests/                    # Test suite
│   ├── test_core.py
│   ├── test_config.py
│   ├── test_gaussian.py
│   ├── test_box.py
│   ├── test_kawase.py
│   └── test_dual.py
├── benchmarks/               # Performance benchmarks
│   └── benchmark_blur.py
├── examples/                 # Example scripts
│   └── example_usage.py
├── README.md
├── pyproject.toml           # Project configuration
├── pytest.ini               # Pytest configuration
└── .gitignore
```

## Adding New Algorithms

To add a new blur algorithm:

1. Create new file in `blur_lib/algorithms/`:

```python
from .base import BlurAlgorithm
import numpy as np
from typing import Any, Dict

class CustomBlur(BlurAlgorithm):
    """Your custom blur algorithm."""
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        # Initialize parameters
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply your custom blur."""
        self._validate_image(image)
        # Your implementation here
        return self._normalize_to_uint8(result)
```

2. Register in `blur_lib/core.py`:

```python
ALGORITHM_MAP = {
    # ... existing algorithms
    "custom": CustomBlur,
}
```

3. Update `blur_lib/config.py` with algorithm defaults and constraints

4. Add tests in `tests/test_custom.py`

## Exception Handling

```python
from blur_lib import BlurProcessor
from blur_lib.exceptions import InvalidConfigError, InvalidImageError

try:
    processor = BlurProcessor({"algorithm": "invalid"})
except InvalidConfigError as e:
    print(f"Config error: {e}")

try:
    processor = BlurProcessor({"algorithm": "gaussian"})
    processor.apply(invalid_image)
except InvalidImageError as e:
    print(f"Image error: {e}")
```

## Performance Tips

1. **Box Blur**: Fastest for small kernels, good for real-time
2. **Kawase Blur**: Excellent for large blur radius
3. **Gaussian Blur**: Best quality, slightly slower
4. **Dual Blur**: Good balance for moderate blur effects

For best performance:
- Use appropriate blur radius for your use case
- Consider image resolution
- Use batch processing when possible
- Profile your specific use case

## Troubleshooting

### Image dimensions issues

```python
# Ensure image is uint8 and has correct shape
assert image.dtype == np.uint8
assert len(image.shape) in (2, 3)  # Grayscale or RGB(A)
assert image.shape[2] in (3, 4) if len(image.shape) == 3  # RGB or RGBA
```

### Configuration validation

```python
from blur_lib import validate_config

try:
    validate_config(config_dict)
except InvalidConfigError as e:
    print(f"Invalid config: {e}")
```

## License

MIT License

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## References

- [Gaussian Blur](https://en.wikipedia.org/wiki/Gaussian_blur)
- [Kawase Blur](https://www.gamedev.net/tutorials/graphics/general/kawase-blur-post-process-shader-3357/)
- [Box Blur](https://en.wikipedia.org/wiki/Box_blur)
- [Multi-scale Blur](https://en.wikipedia.org/wiki/Scale_space)
