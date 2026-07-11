# Camera Calibration Package

A modular, standards-compliant Python package for astronomical camera calibration with altitude-azimuth to pixel coordinate transformations and radial-tangential distortion correction.

## Overview

This package refactors the monolithic `calibration.matrix.ipynb` Jupyter notebook into a structured, distributable Python package. The transformation includes:

- **Modularity**: Separated concerns across multiple modules (projections, distortion, core calibration)
- **Configurability**: All hardcoded parameters are now configurable
- **Documentation**: Complete NumPy-format docstrings with physical units
- **Testing**: Comprehensive unit and integration tests
- **Distribution**: Standard `pyproject.toml` packaging setup

## Package Structure

```
camera_calibration/
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Pin specific versions for reproducibility
├── setup.py                    # Legacy setup file
├── README.md                   # This file
├── src/
│   └── camera_calibration/
│       ├── __init__.py         # Package initialization
│       ├── core.py             # Main CameraCalibrator class
│       ├── models.py           # Data models and configuration
│       ├── projections.py      # Coordinate transformation functions
│       ├── distortion.py       # Radial-tangential distortion models
│       └── io.py               # Data loading and saving utilities
├── tests/
│   ├── conftest.py             # Pytest configuration
│   ├── test_core.py            # Core functionality tests
│   ├── test_projections.py     # Projection function tests
│   ├── test_distortion.py      # Distortion model tests
│   └── test_integration.py     # End-to-end workflow tests
└── examples/
    └── basic_usage.py          # Simple usage example
```

## Installation

### Development Installation

```bash
cd camera_calibration
pip install -e .
```

### With Optional Dependencies

```bash
# For development and testing
pip install -e ".[dev]"

# For machine learning enhancements (neural network optimization)
pip install -e ".[ml]"

# For documentation building
pip install -e ".[docs]"
```

## Quick Start

### Basic Usage

```python
import numpy as np
from camera_calibration import CameraCalibrator

# Load your observation data
azalt = np.array([...])      # Shape: (N, 2), columns: [azimuth (deg), altitude (deg)]
photo = np.array([...])      # Shape: (N, 2), columns: [x (pixels), y (pixels)]

# Create and configure calibrator
calibrator = CameraCalibrator(
    initial_center_x=1053.0,
    initial_center_y=1063.0,
    initial_scale=983.0,
    initial_north_bias=2.716  # radians
)

# Load data
calibrator.load_data(azalt, photo)

# Perform calibration
calibrator.fit_projection()
calibrator.fit_distortion()
result = calibrator.fit_global()

# Get predictions
predicted_photo = calibrator.predict(azalt)
errors = photo - predicted_photo
print(f"RMS error: {np.sqrt((errors ** 2).sum(axis=1)).mean():.3f} pixels")
```

### Using Coordinate Transforms

```python
from camera_calibration import (
    azalt_to_polar, photo_to_polar, polar_to_photo, polar_to_azalt
)

# Convert Alt-Az to polar coordinates
azalt = np.array([[0, 45], [90, 60]])
polar = azalt_to_polar(azalt, scale=983.0, north_bias=2.716)

# Convert photo coordinates to polar
photo = np.array([[100, 200], [500, 600]])
photo_polar = photo_to_polar(photo, center_x=1053, center_y=1063)

# Inverse transformations
photo_back = polar_to_photo(polar, center_x=1053, center_y=1063)
azalt_back = polar_to_azalt(polar, scale=983.0, north_bias=2.716)
```

## Core Concepts

### Calibration Workflow

The calibration process follows this sequence:

1. **Data Loading**: Load paired observations (Alt-Az vs photo coordinates)
2. **Polar Conversion**: Convert both coordinate systems to polar
3. **Projection Fitting**: Fit radial projection model
4. **Distortion Fitting**: Fit radial-tangential distortion terms
5. **Global Optimization**: Jointly optimize all parameters
6. **Validation**: Compute residuals and error metrics

### Physical Units

All functions explicitly document their input/output units:

- **Angles**: degrees (input) or radians (internal)
- **Pixel Coordinates**: pixels (integers or floats)
- **Scale Factors**: pixels/radian or dimensionless
- **Rotation Angles**: radians

### Calibration Parameters

The calibration involves several parameter groups:

#### Coordinate System Parameters

- `center_x`, `center_y`: Image center in pixels
- `scale`: Radial scale factor (pixels)
- `north_bias`: Rotation angle (radians)

#### Projection Parameters (5 coefficients)

Fit a polynomial radial projection: `rho_photo = k0*rho + k1*rho^3 + k2*rho^5 + k3*rho^7 + k4*rho^9`

#### Radial-Tangential Distortion Parameters (7 coefficients each for rho and theta)

Model optical distortion with:

- Radial terms: polynomial in radius
- Tangential terms: sinusoidal functions

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Category

```bash
# Core functionality tests
pytest tests/test_core.py -v

# Projection tests
pytest tests/test_projections.py -v

# Distortion tests
pytest tests/test_distortion.py -v

# End-to-end tests
pytest tests/test_integration.py -v
```

### Generate Coverage Report

```bash
pytest tests/ --cov=camera_calibration --cov-report=html
open htmlcov/index.html
```

## Key Differences from Original Notebook

### Original Notebook (`calibration.matrix.ipynb`)

- Procedural, linear flow
- Hardcoded parameter values
- Manual step-by-step fitting
- Limited reusability
- No error handling

### Refactored Package

- Modular architecture with clear responsibilities
- Configurable parameters and flexible workflows
- Encapsulated calibration logic in `CameraCalibrator` class
- Reusable functions for coordinate transforms
- Comprehensive error handling and validation
- Full documentation with physical units
- Extensive test coverage

## Validation Against Original

The refactored package includes integration tests that:

1. **Reproduce Original Results**: Synthetic data generation matches the notebook's approach
2. **Parameter Equivalence**: Calibration parameters are equivalent when starting from identical data
3. **Numerical Accuracy**: Prediction errors match within floating-point precision
4. **Edge Cases**: Handle boundary conditions like extreme altitudes

To validate against the original notebook:

```bash
# Generate synthetic data matching the original
python -c "
import numpy as np
from camera_calibration import CameraCalibrator

# Create synthetic data similar to the original
# ... (see examples/basic_usage.py for full example)
"

# Run integration tests
pytest tests/test_integration.py::TestEndToEndCalibration -v
```

## Dependencies

### Core Dependencies

- `numpy>=1.19.0`: Numerical computing
- `scipy>=1.5.0`: Scientific computing (curve fitting)
- `pandas>=1.0.0`: Data manipulation
- `scikit-learn>=0.24.0`: Machine learning utilities

### Optional Dependencies

- `torch>=1.9.0`: For neural network-based refinement (ML mode)
- `pytest>=6.0`: For testing
- `sphinx>=4.0`: For documentation

## Contributing

To extend or modify the package:

1. **Add new features**: Create new modules in `src/camera_calibration/`
2. **Write tests**: Add corresponding tests in `tests/`
3. **Update documentation**: Add docstrings and update README
4. **Run tests**: Ensure all tests pass before committing

## License

MIT License

## Citation

If you use this package, please cite the original work and acknowledge the refactoring:

```bibtex
@software{camera_calibration_2026,
  title={Camera Calibration Package},
  author={Astronomy Research Team},
  year={2026},
  note={Refactored from original notebook: calibration.matrix.ipynb}
}
```

## Authors

- Refactored by: AI Agent (astro-refactor)
- Original work: Astronomy Research Team

## Support

For issues, questions, or contributions, please open an issue or pull request.
