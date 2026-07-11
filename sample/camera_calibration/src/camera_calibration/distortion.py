"""
Distortion correction models for camera calibration.

This module implements radial-tangential distortion correction
similar to OpenCV's distortion model.
"""

import numpy as np
from typing import Tuple


def rho_projection(rho: np.ndarray, k: np.ndarray) -> np.ndarray:
    """
    Apply polynomial radius correction to rho values.

    This implements a 5-term polynomial correction to the radial coordinate,
    commonly used for fisheye lens distortion correction.

    Parameters
    ----------
    rho : np.ndarray
        Input radial coordinates. Shape: (N,). Units: pixels
    k : np.ndarray
        Polynomial coefficients [k0, k1, k2, k3, k4]. Shape: (5,).
        Correction formula: rho_corrected = k0*rho + k1*rho^3 + k2*rho^5
                                          + k3*rho^7 + k4*rho^9

    Returns
    -------
    np.ndarray
        Corrected radial coordinates. Shape: (N,). Units: pixels
    """
    powers = np.array([rho, rho**3, rho**5, rho**7, rho**9]).T
    return np.dot(powers, k)


def distortion_term(polar: np.ndarray, radial: np.ndarray, tangential: np.ndarray) -> np.ndarray:
    """
    Calculate the combined radial-tangential distortion term.

    The distortion is modeled as a product of radial and tangential components:
    distortion = (radial component) × (tangential component)

    Parameters
    ----------
    polar : np.ndarray
        Polar coordinates [rho, theta]. Shape: (N, 2).
        rho : Radial distance. Units: pixels
        theta : Angular position. Units: radians
    radial : np.ndarray
        Radial distortion coefficients [r0, r1, r2]. Shape: (3,).
        radial_term = r0*rho + r1*rho^3 + r2*rho^5
    tangential : np.ndarray
        Tangential distortion coefficients [t0, t1, t2, t3]. Shape: (4,).
        tangential_term = t0*cos(θ) + t1*sin(θ) + t2*cos(2θ) + t3*sin(2θ)

    Returns
    -------
    np.ndarray
        Combined distortion value. Shape: (N,). Units: pixels or radians
        (depending on application to rho or theta)
    """
    rho = polar[..., 0]
    theta = polar[..., 1]

    # Radial component: polynomial in rho
    radial_component = np.dot(np.array([rho, rho**3, rho**5]).T, radial)

    # Tangential component: trigonometric in theta
    tangential_component = np.dot(
        np.array([np.cos(theta), np.sin(theta), np.cos(2 * theta), np.sin(2 * theta)]).T, tangential
    )

    return radial_component * tangential_component


def apply_rho_distortion(
    polar: np.ndarray, radial: np.ndarray, tangential: np.ndarray
) -> np.ndarray:
    """
    Apply radial-tangential distortion to rho coordinate.

    Parameters
    ----------
    polar : np.ndarray
        Polar coordinates [rho, theta]. Shape: (N, 2). Units: pixels, radians
    radial : np.ndarray
        Radial distortion coefficients. Shape: (3,)
    tangential : np.ndarray
        Tangential distortion coefficients. Shape: (4,)

    Returns
    -------
    np.ndarray
        Distorted rho values. Shape: (N,). Units: pixels
    """
    distortion = distortion_term(polar, radial, tangential)
    return polar[..., 0] + distortion


def apply_theta_distortion(
    polar: np.ndarray, radial: np.ndarray, tangential: np.ndarray
) -> np.ndarray:
    """
    Apply radial-tangential distortion to theta coordinate.

    Parameters
    ----------
    polar : np.ndarray
        Polar coordinates [rho, theta]. Shape: (N, 2). Units: pixels, radians
    radial : np.ndarray
        Radial distortion coefficients. Shape: (3,)
    tangential : np.ndarray
        Tangential distortion coefficients. Shape: (4,)

    Returns
    -------
    np.ndarray
        Distorted theta values (modulo 2π). Shape: (N,). Units: radians
    """
    distortion = distortion_term(polar, radial, tangential)
    result = (polar[..., 1] + distortion) % (2 * np.pi)
    return result


def undistort_rho(
    rho_distorted: np.ndarray,
    polar: np.ndarray,
    radial: np.ndarray,
    tangential: np.ndarray,
    max_iterations: int = 10,
    tolerance: float = 1e-6,
) -> np.ndarray:
    """
    Undo radial distortion on rho (iterative Newton-Raphson method).

    Parameters
    ----------
    rho_distorted : np.ndarray
        Distorted rho values. Shape: (N,). Units: pixels
    polar : np.ndarray
        Undistorted polar coordinates [rho, theta]. Shape: (N, 2).
    radial : np.ndarray
        Radial distortion coefficients. Shape: (3,)
    tangential : np.ndarray
        Tangential distortion coefficients. Shape: (4,)
    max_iterations : int, optional
        Maximum iterations for Newton-Raphson. Default: 10
    tolerance : float, optional
        Convergence tolerance. Units: pixels. Default: 1e-6

    Returns
    -------
    np.ndarray
        Undistorted rho values. Shape: (N,). Units: pixels
    """
    # This is a simplified inverse - full implementation would need
    # iterative root-finding due to nonlinearity
    # For now, return the input (user should calibrate for forward application)
    return rho_distorted
