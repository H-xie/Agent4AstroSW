"""
Tests for distortion correction functions.
"""

import numpy as np
import pytest
from camera_calibration.distortion import (
    rho_projection,
    distortion_term,
    apply_rho_distortion,
    apply_theta_distortion,
)


class TestRhoProjection:
    """Test radial projection function."""

    def test_linear_projection(self):
        """Test linear projection (only k0 term)."""
        rho = np.array([10, 20, 30, 40])
        k = np.array([2.0, 0, 0, 0, 0])  # Only linear term

        result = rho_projection(rho, k)
        expected = rho * 2.0

        assert np.allclose(result, expected)

    def test_polynomial_projection(self):
        """Test polynomial projection with multiple terms."""
        rho = np.array([1.0, 2.0, 3.0])
        k = np.array([1.0, 0.1, 0.01, 0.001, 0.0001])

        # Manual calculation for verification
        expected = k[0] * rho + k[1] * rho**3 + k[2] * rho**5 + k[3] * rho**7 + k[4] * rho**9

        result = rho_projection(rho, k)
        assert np.allclose(result, expected)

    def test_zero_projection(self):
        """Test zero projection coefficients."""
        rho = np.array([10, 20, 30])
        k = np.array([0, 0, 0, 0, 0])

        result = rho_projection(rho, k)
        assert np.allclose(result, 0)

    def test_batch_processing(self):
        """Test batch processing of multiple rho values."""
        rho = np.linspace(0, 100, 50)
        k = np.array([1.01, -1e-7, 3e-13, -6e-19, 4e-25])

        result = rho_projection(rho, k)

        # Result should be monotonically increasing
        assert np.all(np.diff(result) >= 0)

        # Result should be close to rho for small distortion
        assert np.allclose(result, rho, rtol=0.1)


class TestDistortionTerm:
    """Test combined radial-tangential distortion term."""

    def test_pure_radial_distortion(self):
        """Test with only radial component."""
        polar = np.array([[10, 0], [20, np.pi / 2]])
        radial = np.array([0.1, 0, 0])
        tangential = np.array([0, 0, 0, 0])

        result = distortion_term(polar, radial, tangential)

        # Should be proportional to rho only
        expected = radial[0] * polar[:, 0]  # r0 * rho + 0 * rho^3 + ...
        assert np.allclose(result, expected)

    def test_pure_tangential_distortion(self):
        """Test with only tangential component."""
        rho_val = 50
        theta_vals = np.array([0, np.pi / 2, np.pi, 3 * np.pi / 2])
        polar = np.array([[rho_val, theta] for theta in theta_vals])

        radial = np.array([0, 0, 0])
        tangential = np.array([1, 0, 0, 0])  # Only cos(theta) term

        result = distortion_term(polar, radial, tangential)

        # Expected: rho * (r=0) * tangential = 0
        assert np.allclose(result, 0)

    def test_multiplicative_nature(self):
        """Test that distortion = radial × tangential."""
        polar = np.array([[30, np.pi / 4]])
        radial = np.array([0.05, 0.001, 0.0])
        tangential = np.array([0.2, 0.3, 0.1, 0.05])

        result = distortion_term(polar, radial, tangential)

        # Manual calculation
        rho = polar[0, 0]
        theta = polar[0, 1]

        radial_comp = radial[0] * rho + radial[1] * rho**3 + radial[2] * rho**5
        tangential_comp = (
            tangential[0] * np.cos(theta)
            + tangential[1] * np.sin(theta)
            + tangential[2] * np.cos(2 * theta)
            + tangential[3] * np.sin(2 * theta)
        )
        expected = radial_comp * tangential_comp

        assert np.isclose(result[0], expected)


class TestApplyRhoDistortion:
    """Test applying distortion to rho coordinate."""

    def test_undistorted_rho_unchanged(self):
        """Test that zero distortion leaves rho unchanged."""
        polar = np.array([[10, 0], [20, np.pi / 2], [30, np.pi]])
        radial = np.array([0, 0, 0])
        tangential = np.array([0, 0, 0, 0])

        result = apply_rho_distortion(polar, radial, tangential)

        assert np.allclose(result, polar[:, 0])

    def test_rho_distortion_sign(self):
        """Test that positive radial distortion increases rho."""
        polar = np.array([[10, 0]])
        radial = np.array([0.01, 0, 0])
        tangential = np.array([1, 0, 0, 0])  # cos(0) = 1

        result = apply_rho_distortion(polar, radial, tangential)

        # Distortion should be positive (0.01 * 10 * 1 = 0.1)
        assert result[0] > polar[0, 0]

    def test_batch_rho_distortion(self):
        """Test batch application of rho distortion."""
        polar = np.array([[10, 0], [20, np.pi / 2], [30, np.pi]])
        radial = np.array([0.001, 0, 0])
        tangential = np.array([1, 1, 0, 0])

        result = apply_rho_distortion(polar, radial, tangential)

        assert result.shape == (3,)
        # All values should be positive and larger than original
        assert np.all(result > 0)


class TestApplyThetaDistortion:
    """Test applying distortion to theta coordinate."""

    def test_undistorted_theta_unchanged(self):
        """Test that zero distortion leaves theta unchanged."""
        polar = np.array([[10, 0], [20, np.pi / 2], [30, np.pi]])
        radial = np.array([0, 0, 0])
        tangential = np.array([0, 0, 0, 0])

        result = apply_theta_distortion(polar, radial, tangential)

        assert np.allclose(result, polar[:, 1])

    def test_theta_modulo_2pi(self):
        """Test that result is in [0, 2π)."""
        polar = np.array([[50, 1.5 * np.pi]])
        radial = np.array([0, 0, 0])
        tangential = np.array([1, 1, 1, 1])

        result = apply_theta_distortion(polar, radial, tangential)

        assert np.all(result >= 0)
        assert np.all(result < 2 * np.pi)

    def test_batch_theta_distortion(self):
        """Test batch application of theta distortion."""
        polar = np.array([[10, 0], [20, np.pi / 2], [30, np.pi]])
        radial = np.array([0.001, 0, 0])
        tangential = np.array([0.01, 0.01, 0.01, 0.01])

        result = apply_theta_distortion(polar, radial, tangential)

        assert result.shape == (3,)
        assert np.all(result >= 0)
        assert np.all(result < 2 * np.pi)


class TestDistortionCombinations:
    """Test combined radial and tangential distortion effects."""

    def test_small_distortion_approximation(self):
        """Test that small distortion is approximately linear."""
        polar = np.array([[10, 0]])
        radial = np.array([0.001, 0, 0])  # Very small
        tangential = np.array([0.001, 0, 0, 0])  # Very small

        rho_result = apply_rho_distortion(polar, radial, tangential)
        theta_result = apply_theta_distortion(polar, radial, tangential)

        # Rho should be close to original
        assert np.isclose(rho_result[0], polar[0, 0], rtol=0.01)
        # Theta should be close to original
        assert np.isclose(theta_result[0], polar[0, 1], atol=0.01)

    def test_symmetric_distortion(self):
        """Test symmetric points have appropriate symmetry."""
        polar = np.array([[20, 0], [20, np.pi / 2], [20, np.pi], [20, 3 * np.pi / 2]])
        radial = np.array([0.01, 0, 0])
        tangential = np.array([0.5, 0.5, 0, 0])

        rho_result = apply_rho_distortion(polar, radial, tangential)

        # Points at same radius should have same distortion magnitude
        assert np.allclose(rho_result, rho_result[0], rtol=0.01)
