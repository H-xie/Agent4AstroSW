"""
Integration tests using real or realistic data.

These tests verify the calibration workflow end-to-end.
"""

import numpy as np
import pytest
from pathlib import Path
from camera_calibration.core import CameraCalibrator
from camera_calibration.io import CalibrationIO
from camera_calibration.models import CalibrationParams


class TestEndToEndCalibration:
    """End-to-end calibration workflow tests."""

    @pytest.fixture
    def synthetic_calibration_data(self):
        """Generate synthetic but realistic calibration data."""
        np.random.seed(123)

        # Parameters used to generate synthetic data
        true_params = {
            "center_x": 1053,
            "center_y": 1063,
            "scale": 983,
            "north_bias": 2.716,
            "k": [0.02, -1e-7, 3e-13, -6e-19, 4e-25],
            "dist_rho": [-0.0035, 1e-8, -1e-14, -2.49, -1.99, -0.014, -0.036],
            "dist_theta": [-3.3e-4, 1.3e-9, -1.4e-15, -0.093, 0.098, 0.026, -0.0096],
        }

        # Generate random Alt-Az coordinates
        n_points = 50
        azimuths = np.random.uniform(0, 360, n_points)
        altitudes = np.random.uniform(20, 85, n_points)
        azalt = np.column_stack([azimuths, altitudes])

        # Generate synthetic photo coordinates
        # (In real case, these would be measured)
        cal = CameraCalibrator(
            initial_center_x=true_params["center_x"],
            initial_center_y=true_params["center_y"],
            initial_scale=true_params["scale"],
            initial_north_bias=true_params["north_bias"],
        )

        # Create synthetic data using simplified forward model
        from camera_calibration.projections import azalt_to_polar, polar_to_photo
        from camera_calibration.distortion import (
            rho_projection,
            apply_rho_distortion,
            apply_theta_distortion,
        )

        polar_azalt = azalt_to_polar(
            azalt, scale=true_params["scale"], north_bias=true_params["north_bias"]
        )

        # Apply projection
        rho_proj = rho_projection(polar_azalt[:, 0], true_params["k"])
        polar_proj = polar_azalt.copy()
        polar_proj[:, 0] = rho_proj

        # Apply distortion
        rho_dist = apply_rho_distortion(
            polar_proj, true_params["dist_rho"][:3], true_params["dist_rho"][3:]
        )
        theta_dist = apply_theta_distortion(
            polar_proj, true_params["dist_theta"][:3], true_params["dist_theta"][3:]
        )

        polar_final = np.column_stack([rho_dist, theta_dist])
        photo = polar_to_photo(
            polar_final, center_x=true_params["center_x"], center_y=true_params["center_y"]
        )

        # Add small noise to make realistic
        photo += np.random.normal(0, 0.5, photo.shape)

        return azalt, photo, true_params

    def test_full_calibration_workflow(self, synthetic_calibration_data):
        """Test complete calibration pipeline."""
        azalt, photo, true_params = synthetic_calibration_data

        # Create calibrator
        cal = CameraCalibrator(
            initial_center_x=true_params["center_x"],
            initial_center_y=true_params["center_y"],
            initial_scale=true_params["scale"],
            initial_north_bias=true_params["north_bias"],
        )

        # Load data
        cal.load_data(azalt, photo)

        # Fit stages
        proj_result = cal.fit_projection()
        assert proj_result["residual_mean"] < 10  # Should fit reasonably well

        dist_result = cal.fit_distortion()
        assert dist_result["rho"]["residual_mean"] < 5

        full_params = cal.global_fit()
        assert full_params.shape == (23,)

        # Evaluate
        eval_result = cal.evaluate()

        # Check that RMS error is reasonable (noise was ~0.5 pixels)
        assert eval_result.rms_error < 2.0

    def test_calibration_parameters_recovery(self, synthetic_calibration_data):
        """Test that fitted parameters are close to true parameters."""
        azalt, photo, true_params = synthetic_calibration_data

        cal = CameraCalibrator(
            initial_center_x=true_params["center_x"],
            initial_center_y=true_params["center_y"],
            initial_scale=true_params["scale"],
            initial_north_bias=true_params["north_bias"],
        )

        cal.load_data(azalt, photo)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        params = cal.get_calibration_params()

        # Check coordinate system parameters (should be very close)
        assert np.isclose(params.coord_system.center_x, true_params["center_x"], atol=2)
        assert np.isclose(params.coord_system.center_y, true_params["center_y"], atol=2)
        assert np.isclose(params.coord_system.scale, true_params["scale"], rtol=0.01)

    def test_prediction_accuracy(self, synthetic_calibration_data):
        """Test prediction accuracy on training data."""
        azalt, photo, _ = synthetic_calibration_data

        cal = CameraCalibrator()
        cal.load_data(azalt, photo)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        predictions = cal.predict(azalt)
        errors = predictions - photo

        # Check accuracy
        rms_error = np.sqrt(np.mean(errors**2))
        assert rms_error < 1.0  # Should be small on training data

        # Check that predictions are within image bounds
        assert np.all(predictions[:, 0] > 0)
        assert np.all(predictions[:, 0] < 2000)
        assert np.all(predictions[:, 1] > 0)
        assert np.all(predictions[:, 1] < 2000)


class TestIOOperations:
    """Test I/O operations for calibration data."""

    def test_calibration_params_round_trip(self, sample_calibration_params, tmp_path):
        """Test saving and loading calibration parameters."""
        output_file = tmp_path / "cal_params.json"

        # Save
        CalibrationIO.save_calibration_params(sample_calibration_params, str(output_file))

        # Load
        loaded = CalibrationIO.load_calibration_params(str(output_file))

        # Verify
        assert loaded.coord_system.center_x == sample_calibration_params.coord_system.center_x
        assert loaded.coord_system.center_y == sample_calibration_params.coord_system.center_y
        assert np.isclose(loaded.projection.k0, sample_calibration_params.projection.k0)

    def test_result_saving(self, sample_azalt_coordinates, sample_photo_coordinates, tmp_path):
        """Test saving calibration results."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        result = cal.evaluate()
        output_file = tmp_path / "results.csv"

        # Save
        CalibrationIO.save_result(result, str(output_file), azalt_original=sample_azalt_coordinates)

        # Verify file exists and has content
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_evaluation_summary_saving(
        self, sample_azalt_coordinates, sample_photo_coordinates, tmp_path
    ):
        """Test saving evaluation summary."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        result = cal.evaluate()
        output_file = tmp_path / "summary.json"

        # Save
        CalibrationIO.save_evaluation_summary(result, str(output_file))

        # Verify file exists
        assert output_file.exists()

        # Load and verify contents
        import json

        with open(output_file) as f:
            summary = json.load(f)

        assert "rms_error_pixels" in summary
        assert "max_error_pixels" in summary
        assert summary["n_points"] == len(sample_azalt_coordinates)


class TestDataConsistency:
    """Test data consistency across transformations."""

    def test_forward_backward_consistency(self, sample_azalt_coordinates):
        """Test that forward-backward transformations are consistent."""
        from camera_calibration.projections import azalt_to_polar, polar_to_azalt

        scale = 983.0
        north_bias = np.deg2rad(155.6)

        # Forward
        polar = azalt_to_polar(sample_azalt_coordinates, scale, north_bias)

        # Backward
        recovered = polar_to_azalt(polar, scale, north_bias)

        # Check consistency
        assert np.allclose(sample_azalt_coordinates, recovered, rtol=1e-10)

    def test_coordinate_system_independence(self, sample_azalt_coordinates):
        """Test that different coordinate centers give consistent calibration."""
        from camera_calibration.projections import photo_to_polar, polar_to_photo

        # Two different centers
        center1 = (1000, 1000)
        center2 = (1100, 1100)

        # Synthetic photo coordinates (arbitrary for this test)
        photo = np.array([[1050, 1050], [1100, 1100], [1200, 1150]])

        # Convert with different centers
        polar1 = photo_to_polar(photo, center1[0], center1[1])
        recovered1 = polar_to_photo(polar1, center1[0], center1[1])

        polar2 = photo_to_polar(photo, center2[0], center2[1])
        recovered2 = polar_to_photo(polar2, center2[0], center2[1])

        # Both should recover original (with their respective centers)
        assert np.allclose(photo, recovered1, rtol=1e-10)
        assert np.allclose(photo, recovered2, rtol=1e-10)
