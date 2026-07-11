"""
Coordinate transformation and projection functions.

This module handles conversion between different coordinate systems:
- Horizontal (Alt-Az) ↔ Polar (rho, theta)
- Photo coordinates ↔ Polar coordinates
"""

from typing import Tuple
import numpy as np


def azalt_to_polar(azalt: np.ndarray, scale: float = 983.0, north_bias: float = 0.0) -> np.ndarray:
    """
    Convert horizontal (altitude-azimuth) coordinates to polar coordinates.

    The transformation implements a fisheye-like projection where angular
    distance from zenith maps linearly to image radius.

    Parameters
    ----------
    azalt : np.ndarray
        Array of [azimuth, altitude] pairs. Shape: (N, 2).
        azimuth : float
            Azimuth angle. Units: degrees. Range: [0, 360)
        altitude : float
            Altitude angle above horizon. Units: degrees. Range: [0, 90]
    scale : float, optional
        Radial scale factor. Units: pixels/radian (approximately).
        Default: 983.0 (typical for the camera system)
    north_bias : float, optional
        Rotation angle from image X-axis to North.
        Units: radians. Default: 0.0

    Returns
    -------
    np.ndarray
        Polar coordinates [rho, theta]. Shape: (N, 2).
        rho : float
            Radial distance from image center. Units: pixels
        theta : float
            Angular position. Units: radians. Range: [0, 2π]

    Notes
    -----
    The projection assumes:
    - Zenith (alt=90°) maps to rho=0
    - Horizon (alt=0°) maps to maximum rho = scale * π/2
    """
    az = azalt[..., 0]
    alt = azalt[..., 1]

    # Angular zenith distance in radians, normalized to [0, π/2]
    rho = np.deg2rad(90 - alt) / (np.pi / 2)
    # Convert to pixel radius
    rho *= scale

    # Azimuth to theta with north bias correction
    theta = np.deg2rad(az)
    theta += north_bias
    theta %= 2 * np.pi

    return np.array([rho, theta]).T


def photo_to_polar(
    photo: np.ndarray, center_x: float = 1053.0, center_y: float = 1063.0
) -> np.ndarray:
    """
    Convert photo coordinates (x, y) to polar coordinates (rho, theta).

    Parameters
    ----------
    photo : np.ndarray
        Array of [x, y] pixel coordinates. Shape: (N, 2).
        x : float
            Horizontal pixel coordinate. Units: pixels
        y : float
            Vertical pixel coordinate. Units: pixels
    center_x : float, optional
        X coordinate of image center. Units: pixels. Default: 1053.0
    center_y : float, optional
        Y coordinate of image center. Units: pixels. Default: 1063.0

    Returns
    -------
    np.ndarray
        Polar coordinates [rho, theta]. Shape: (N, 2).
        rho : float
            Distance from image center. Units: pixels
        theta : float
            Angle from positive X-axis. Units: radians. Range: [0, 2π]
    """
    # Translate to center
    x = photo[..., 0] - center_x
    y = photo[..., 1] - center_y

    # Calculate polar coordinates
    rho = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x) % (2 * np.pi)

    return np.array([rho, theta]).T


def polar_to_photo(
    polar: np.ndarray, center_x: float = 1053.0, center_y: float = 1063.0
) -> np.ndarray:
    """
    Convert polar coordinates back to photo (pixel) coordinates.

    Parameters
    ----------
    polar : np.ndarray
        Array of [rho, theta] polar coordinates. Shape: (N, 2).
        rho : float
            Radial distance from center. Units: pixels
        theta : float
            Angular position. Units: radians
    center_x : float, optional
        X coordinate of image center. Units: pixels. Default: 1053.0
    center_y : float, optional
        Y coordinate of image center. Units: pixels. Default: 1063.0

    Returns
    -------
    np.ndarray
        Photo coordinates [x, y]. Shape: (N, 2). Units: pixels
    """
    rho = polar[..., 0]
    theta = polar[..., 1]

    x = rho * np.cos(theta) + center_x
    y = rho * np.sin(theta) + center_y

    return np.array([x, y]).T


def polar_to_azalt(polar: np.ndarray, scale: float = 983.0, north_bias: float = 0.0) -> np.ndarray:
    """
    Convert polar coordinates back to horizontal (altitude-azimuth) coordinates.

    Parameters
    ----------
    polar : np.ndarray
        Array of [rho, theta] polar coordinates. Shape: (N, 2).
        rho : float
            Radial distance in pixels. Units: pixels
        theta : float
            Angular position. Units: radians
    scale : float, optional
        Radial scale factor (must match the forward transformation).
        Units: pixels. Default: 983.0
    north_bias : float, optional
        Rotation angle from image X-axis to North.
        Units: radians. Default: 0.0

    Returns
    -------
    np.ndarray
        Horizontal coordinates [azimuth, altitude]. Shape: (N, 2).
        Units: degrees
    """
    rho = polar[..., 0]
    theta = polar[..., 1]

    # Inverse of zenith distance mapping
    zenith_dist_rad = (rho / scale) * (np.pi / 2)
    alt = 90 - np.rad2deg(zenith_dist_rad)

    # Remove north bias and convert to azimuth
    az = theta - north_bias
    az %= 2 * np.pi
    az = np.rad2deg(az)

    return np.array([az, alt]).T
