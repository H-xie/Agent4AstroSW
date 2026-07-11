"""
Data models and calibration parameters for camera calibration.

This module defines the core data structures used throughout the camera calibration
package, including coordinate systems, calibration parameters, and results.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Tuple
import numpy as np


@dataclass
class CoordinateSystemParams:
    """
    Parameters defining the coordinate system transformation.

    Attributes
    ----------
    center_x : float
        Center X pixel coordinate. Units: pixels
    center_y : float
        Center Y pixel coordinate. Units: pixels
    scale : float
        Radial scale factor converting angular radius to pixel radius.
        Units: pixels/radian (approximately)
    north_bias : float
        Rotation angle offset from image coordinate system.
        Units: radians
    """

    center_x: float
    center_y: float
    scale: float
    north_bias: float


@dataclass
class ProjectionParams:
    """
    Parameters for polar coordinate projection (radius correction).

    Attributes
    ----------
    k0, k1, k2, k3, k4 : float
        Polynomial coefficients for rho projection:
        rho_corrected = k0*rho + k1*rho^3 + k2*rho^5 + k3*rho^7 + k4*rho^9
    """

    k0: float
    k1: float
    k2: float
    k3: float
    k4: float

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "ProjectionParams":
        """Create from numpy array of coefficients."""
        return cls(*arr)

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.k0, self.k1, self.k2, self.k3, self.k4])


@dataclass
class RadialTangentialDistortionParams:
    """
    Parameters for radial-tangential distortion correction.

    Attributes
    ----------
    radial0, radial1, radial2 : float
        Radial distortion coefficients (polynomial terms in rho)
        radial_term = radial0*rho + radial1*rho^3 + radial2*rho^5
    tan0, tan1, tan2, tan3 : float
        Tangential distortion coefficients (trigonometric terms in theta)
        tangential_term = tan0*cos(theta) + tan1*sin(theta)
                         + tan2*cos(2*theta) + tan3*sin(2*theta)
    """

    radial0: float
    radial1: float
    radial2: float
    tan0: float
    tan1: float
    tan2: float
    tan3: float

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "RadialTangentialDistortionParams":
        """Create from numpy array."""
        return cls(*arr)

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array(
            [self.radial0, self.radial1, self.radial2, self.tan0, self.tan1, self.tan2, self.tan3]
        )


@dataclass
class CalibrationParams:
    """
    Complete set of calibration parameters.

    This combines all parameter types needed for full camera calibration.
    """

    coord_system: CoordinateSystemParams
    projection: ProjectionParams
    distortion_rho: RadialTangentialDistortionParams
    distortion_theta: RadialTangentialDistortionParams

    @property
    def as_flat_array(self) -> np.ndarray:
        """Convert all parameters to a flat numpy array for optimization."""
        return np.concatenate(
            [
                np.array([self.coord_system.scale, self.coord_system.north_bias]),
                self.projection.to_array(),
                self.distortion_rho.to_array(),
                self.distortion_theta.to_array(),
                np.array([self.coord_system.center_x, self.coord_system.center_y]),
            ]
        )

    @classmethod
    def from_flat_array(
        cls, arr: np.ndarray, coord_system: Optional[CoordinateSystemParams] = None
    ) -> "CalibrationParams":
        """
        Create from flat parameter array.

        Parameters
        ----------
        arr : np.ndarray
            Flat array of parameters in order: scale, north_bias, proj(5),
            dist_rho(7), dist_theta(7), center_x, center_y
        coord_system : CoordinateSystemParams, optional
            If provided, only update projection and distortion parameters
        """
        scale, north_bias = arr[0:2]
        proj_params = arr[2:7]
        dist_rho_params = arr[7:14]
        dist_theta_params = arr[14:21]
        center_x, center_y = arr[21:23]

        if coord_system is None:
            coord_system = CoordinateSystemParams(
                center_x=center_x, center_y=center_y, scale=scale, north_bias=north_bias
            )

        return cls(
            coord_system=coord_system,
            projection=ProjectionParams.from_array(proj_params),
            distortion_rho=RadialTangentialDistortionParams.from_array(dist_rho_params),
            distortion_theta=RadialTangentialDistortionParams.from_array(dist_theta_params),
        )


@dataclass
class CalibrationResult:
    """
    Result of camera calibration.

    Attributes
    ----------
    predicted_photo_x : np.ndarray
        Predicted pixel X coordinates. Shape: (N,). Units: pixels
    predicted_photo_y : np.ndarray
        Predicted pixel Y coordinates. Shape: (N,). Units: pixels
    error_x : np.ndarray
        Residual error in X. Shape: (N,). Units: pixels
    error_y : np.ndarray
        Residual error in Y. Shape: (N,). Units: pixels
    rms_error : float
        RMS of total positional error. Units: pixels
    max_error : float
        Maximum residual error magnitude. Units: pixels
    """

    predicted_photo_x: np.ndarray
    predicted_photo_y: np.ndarray
    error_x: np.ndarray
    error_y: np.ndarray

    @property
    def rms_error(self) -> float:
        """Calculate RMS error in pixels."""
        error_magnitude = np.sqrt(self.error_x**2 + self.error_y**2)
        return float(np.mean(error_magnitude))

    @property
    def max_error(self) -> float:
        """Calculate maximum error magnitude in pixels."""
        error_magnitude = np.sqrt(self.error_x**2 + self.error_y**2)
        return float(np.max(error_magnitude))
