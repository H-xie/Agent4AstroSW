"""
Camera Calibration Package

A modular, standards-compliant Python package for astronomical camera calibration.
Supports altitude-azimuth to pixel coordinate transformations with radial-tangential
distortion correction.
"""

from .core import CameraCalibrator
from .models import (
    CalibrationParams,
    CalibrationResult,
    CoordinateSystemParams,
    ProjectionParams,
    RadialTangentialDistortionParams,
)
from .io import CalibrationIO
from .projections import azalt_to_polar, photo_to_polar, polar_to_photo, polar_to_azalt
from .distortion import (
    rho_projection,
    distortion_term,
    apply_rho_distortion,
    apply_theta_distortion,
)

__version__ = "0.1.0"

__all__ = [
    "CameraCalibrator",
    "CalibrationParams",
    "CalibrationResult",
    "CoordinateSystemParams",
    "ProjectionParams",
    "RadialTangentialDistortionParams",
    "CalibrationIO",
    "azalt_to_polar",
    "photo_to_polar",
    "polar_to_photo",
    "polar_to_azalt",
    "rho_projection",
    "distortion_term",
    "apply_rho_distortion",
    "apply_theta_distortion",
]
