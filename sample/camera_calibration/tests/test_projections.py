"""
Tests for coordinate projection functions.
"""

import numpy as np
import pytest
from camera_calibration.projections import (
    azalt_to_polar,
    photo_to_polar,
    polar_to_photo,
    polar_to_azalt,
)


class TestAzaltToPolar:
    """Test azimuth-altitude to polar coordinate conversion."""

    def test_zenith_point(self):
        """Test that zenith (alt=90) maps to rho=0."""
        azalt = np.array([[0, 90]])
        polar = azalt_to_polar(azalt)
        assert polar[0, 0] < 0.1  # rho ≈ 0

    def test_horizon_point(self):
        """Test that horizon (alt=0) maps to maximum rho."""
        azalt = np.array([[0, 0]])
        polar = azalt_to_polar(azalt, scale=983.0)
        expected_rho = 983.0 * np.pi / 2  # Maximum radius
        assert np.isclose(polar[0, 0], expected_rho, rtol=0.01)

    def test_batch_conversion(self):
        """Test batch conversion of multiple points."""
        azalt = np.array(
            [
                [0, 90],  # zenith
                [0, 0],  # horizon north
                [90, 0],  # horizon east
                [180, 0],  # horizon south
                [270, 0],  # horizon west
            ]
        )
        polar = azalt_to_polar(azalt, scale=983.0, north_bias=0.0)

        # Check shapes
        assert polar.shape == (5, 2)

        # Zenith should have smallest rho
        assert polar[0, 0] < polar[1:, 0].min()

        # Horizon points should have similar rho magnitude
        horizon_rhos = polar[1:, 0]
        assert np.allclose(horizon_rhos, horizon_rhos[0], rtol=0.1)

    def test_north_bias_application(self):
        """Test that north bias rotates theta."""
        azalt = np.array([[0, 45]])

        polar1 = azalt_to_polar(azalt, north_bias=0.0)
        polar2 = azalt_to_polar(azalt, north_bias=np.pi / 4)

        # Theta should differ by north_bias
        delta_theta = (polar2[0, 1] - polar1[0, 1]) % (2 * np.pi)
        assert np.isclose(delta_theta, np.pi / 4, rtol=1e-10)

    def test_scale_factor(self):
        """Test that scale factor affects rho linearly."""
        azalt = np.array([[0, 45]])

        polar1 = azalt_to_polar(azalt, scale=500)
        polar2 = azalt_to_polar(azalt, scale=1000)

        # Rho should scale linearly
        assert np.isclose(polar2[0, 0] / polar1[0, 0], 2.0, rtol=1e-10)


class TestPhotoToPolar:
    """Test photo pixel to polar coordinate conversion."""

    def test_center_point(self):
        """Test that center coordinates map to rho=0."""
        photo = np.array([[1053, 1063]])
        polar = photo_to_polar(photo, center_x=1053, center_y=1063)

        assert polar[0, 0] < 0.1  # rho ≈ 0

    def test_cardinal_directions(self):
        """Test cardinal direction points."""
        center_x, center_y = 1053, 1063
        radius = 100

        # Points at cardinal directions
        photo = np.array(
            [
                [center_x + radius, center_y],  # East
                [center_x, center_y + radius],  # North
                [center_x - radius, center_y],  # West
                [center_x, center_y - radius],  # South
            ]
        )

        polar = photo_to_polar(photo, center_x=center_x, center_y=center_y)

        # All should have same rho
        assert np.allclose(polar[:, 0], radius, rtol=1e-10)

        # Theta should differ by π/2
        thetas = polar[:, 1]
        for i in range(4):
            delta = (thetas[(i + 1) % 4] - thetas[i]) % (2 * np.pi)
            # Due to atan2 behavior, deltas might be π/2 or 3π/2
            assert np.isclose(delta, np.pi / 2, atol=0.01) or np.isclose(
                delta, 3 * np.pi / 2, atol=0.01
            )

    def test_batch_conversion(self):
        """Test batch conversion."""
        photo = np.array([[1053, 1063], [1100, 1063], [1053, 1100], [1200, 1200]])

        polar = photo_to_polar(photo, center_x=1053, center_y=1063)

        assert polar.shape == (4, 2)
        assert polar[0, 0] < 0.1  # Center is at origin


class TestPolarToPhoto:
    """Test polar to photo coordinate conversion (inverse transform)."""

    def test_round_trip_conversion(self):
        """Test that photo -> polar -> photo recovers original."""
        center_x, center_y = 1053, 1063
        photo_original = np.array([[1100, 1100], [1000, 1150], [1200, 1000], [1053, 1063]])

        polar = photo_to_polar(photo_original, center_x=center_x, center_y=center_y)
        photo_recovered = polar_to_photo(polar, center_x=center_x, center_y=center_y)

        assert np.allclose(photo_original, photo_recovered, rtol=1e-10)


class TestPolarToAzalt:
    """Test polar to Alt-Az coordinate conversion (inverse transform)."""

    def test_round_trip_conversion(self):
        """Test that azalt -> polar -> azalt recovers original."""
        azalt_original = np.array([[0, 45], [90, 60], [180, 30], [270, 75]])

        scale = 983.0
        north_bias = np.deg2rad(155.6)

        polar = azalt_to_polar(azalt_original, scale=scale, north_bias=north_bias)
        azalt_recovered = polar_to_azalt(polar, scale=scale, north_bias=north_bias)

        assert np.allclose(azalt_original, azalt_recovered, rtol=1e-10)

    def test_zenith_altitude(self):
        """Test that rho=0 gives altitude=90."""
        polar = np.array([[0.1, 0.0]])
        azalt = polar_to_azalt(polar, scale=983.0, north_bias=0.0)

        # rho close to 0 should give altitude close to 90
        assert azalt[0, 1] > 85


class TestCoordinateChaining:
    """Test complete coordinate transformation chains."""

    def test_azalt_to_photo_chain(self):
        """Test azalt -> polar -> photo transformation."""
        azalt = np.array([[0, 50], [45, 60], [90, 40]])

        center_x, center_y = 1053, 1063
        scale = 983.0
        north_bias = 0.0

        # Forward chain
        polar_azalt = azalt_to_polar(azalt, scale=scale, north_bias=north_bias)

        # For testing, create synthetic photo coords
        # In real case, these would be observed coordinates
        photo = polar_to_photo(polar_azalt, center_x=center_x, center_y=center_y)

        assert photo.shape == (3, 2)
        assert np.all(photo >= 0)  # Check valid pixel coordinates

    def test_full_round_trip(self):
        """Test complete azalt -> polar -> photo -> polar -> azalt."""
        azalt_original = np.array([[0, 45], [180, 60], [45, 75]])

        center_x, center_y = 1053, 1063
        scale = 983.0
        north_bias = np.deg2rad(155.6)

        # Forward chain
        polar1 = azalt_to_polar(azalt_original, scale=scale, north_bias=north_bias)
        photo = polar_to_photo(polar1, center_x=center_x, center_y=center_y)

        # Backward chain
        polar2 = photo_to_polar(photo, center_x=center_x, center_y=center_y)
        azalt_recovered = polar_to_azalt(polar2, scale=scale, north_bias=north_bias)

        # Check recovery
        assert np.allclose(azalt_original, azalt_recovered, rtol=1e-10)
