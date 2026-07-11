"""
Pytest configuration and shared fixtures.
"""

import pytest
import numpy as np
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))


@pytest.fixture
def sample_azalt_coordinates():
    """Generate sample Alt-Az coordinates."""
    np.random.seed(42)
    azimuths = np.linspace(0, 360, 20, endpoint=False)
    altitudes = np.linspace(30, 80, 20)
    azalt = np.column_stack([azimuths, altitudes])
    return azalt


@pytest.fixture
def sample_photo_coordinates():
    """Generate sample photo coordinates."""
    np.random.seed(42)
    x = np.random.uniform(800, 1300, 20)
    y = np.random.uniform(800, 1300, 20)
    photo = np.column_stack([x, y])
    return photo


@pytest.fixture
def test_data_dir():
    """Return test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_calibration_params():
    """Create sample calibration parameters for testing."""
    from camera_calibration.models import (
        CalibrationParams,
        CoordinateSystemParams,
        ProjectionParams,
        RadialTangentialDistortionParams,
    )

    return CalibrationParams(
        coord_system=CoordinateSystemParams(
            center_x=1053.0, center_y=1063.0, scale=983.0, north_bias=np.deg2rad(155.6)
        ),
        projection=ProjectionParams(k0=0.02, k1=-1e-7, k2=3e-13, k3=-6e-19, k4=4e-25),
        distortion_rho=RadialTangentialDistortionParams(
            radial0=-0.0035,
            radial1=1e-8,
            radial2=-1e-14,
            tan0=-2.49,
            tan1=-1.99,
            tan2=-0.014,
            tan3=-0.036,
        ),
        distortion_theta=RadialTangentialDistortionParams(
            radial0=-3.3e-4,
            radial1=1.3e-9,
            radial2=-1.4e-15,
            tan0=-0.093,
            tan1=0.098,
            tan2=0.026,
            tan3=-0.0096,
        ),
    )
