"""
Tests for core calibration algorithm.
"""

import numpy as np
import pytest
from camera_calibration.core import CameraCalibrator
from camera_calibration.models import CalibrationParams


class TestCameraCalibrator:
    """Test the main calibrator class."""

    def test_initialization(self):
        """Test calibrator initialization with defaults."""
        cal = CameraCalibrator()

        assert cal.center_x == 1053.0
        assert cal.center_y == 1063.0
        assert cal.scale == 983.0
        assert np.isclose(cal.north_bias, 2.716)

    def test_custom_initialization(self):
        """Test calibrator initialization with custom parameters."""
        cal = CameraCalibrator(
            initial_center_x=1000, initial_center_y=1000, initial_scale=1000, initial_north_bias=0
        )

        assert cal.center_x == 1000
        assert cal.center_y == 1000
        assert cal.scale == 1000
        assert cal.north_bias == 0

    def test_load_data(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test loading observation data."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)

        assert cal.azalt_data is not None
        assert cal.photo_data is not None
        assert cal.polar_azalt is not None
        assert cal.polar_photo is not None

        assert cal.azalt_data.shape == sample_azalt_coordinates.shape
        assert cal.photo_data.shape == sample_photo_coordinates.shape

    def test_load_data_mismatched_sizes(self, sample_azalt_coordinates):
        """Test that mismatched data sizes raise error."""
        cal = CameraCalibrator()
        photo = np.random.rand(15, 2)  # Different number of rows

        with pytest.raises(ValueError):
            cal.load_data(sample_azalt_coordinates, photo)

    def test_load_data_wrong_columns(self, sample_azalt_coordinates):
        """Test that wrong number of columns raises error."""
        cal = CameraCalibrator()
        photo = np.random.rand(sample_azalt_coordinates.shape[0], 3)  # 3 columns

        with pytest.raises(ValueError):
            cal.load_data(sample_azalt_coordinates, photo)

    def test_fit_projection_requires_data(self):
        """Test that fit_projection requires loaded data."""
        cal = CameraCalibrator()

        with pytest.raises(ValueError):
            cal.fit_projection()

    def test_fit_projection(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test projection fitting."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)

        result = cal.fit_projection()

        assert "coefficients" in result
        assert "residual_mean" in result
        assert "residual_max" in result

        assert result["coefficients"].shape == (5,)
        assert result["residual_mean"] >= 0
        assert result["residual_max"] >= result["residual_mean"]

    def test_fit_distortion_requires_projection(
        self, sample_azalt_coordinates, sample_photo_coordinates
    ):
        """Test that fit_distortion requires projection."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)

        with pytest.raises(ValueError):
            cal.fit_distortion()

    def test_fit_distortion(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test distortion fitting."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()

        result = cal.fit_distortion()

        assert "rho" in result
        assert "theta" in result

        assert result["rho"]["coefficients"].shape == (7,)
        assert result["theta"]["coefficients"].shape == (7,)

    def test_global_fit_requires_distortion(
        self, sample_azalt_coordinates, sample_photo_coordinates
    ):
        """Test that global_fit requires distortion fitting."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)

        with pytest.raises(ValueError):
            cal.global_fit()

    def test_global_fit(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test complete global fitting workflow."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()

        full_params = cal.global_fit()

        assert full_params.shape == (23,)  # 2 + 5 + 7 + 7 + 2
        assert cal.full_params is not None

    def test_predict_requires_global_fit(self, sample_azalt_coordinates):
        """Test that predict requires global fit."""
        cal = CameraCalibrator()

        with pytest.raises(ValueError):
            cal.predict(sample_azalt_coordinates)

    def test_predict(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test prediction after fitting."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        predictions = cal.predict(sample_azalt_coordinates)

        assert predictions.shape == sample_photo_coordinates.shape
        assert np.all(np.isfinite(predictions))

    def test_evaluate(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test evaluation metrics."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        result = cal.evaluate()

        assert result.predicted_photo_x.shape == (sample_azalt_coordinates.shape[0],)
        assert result.error_x.shape == (sample_azalt_coordinates.shape[0],)
        assert result.rms_error >= 0
        assert result.max_error >= result.rms_error

    def test_get_calibration_params(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test getting calibration parameters object."""
        cal = CameraCalibrator()
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        params = cal.get_calibration_params()

        assert isinstance(params, CalibrationParams)
        assert params.coord_system is not None
        assert params.projection is not None
        assert params.distortion_rho is not None
        assert params.distortion_theta is not None

    def test_calibration_workflow(self, sample_azalt_coordinates, sample_photo_coordinates):
        """Test complete calibration workflow."""
        cal = CameraCalibrator(
            initial_center_x=1053,
            initial_center_y=1063,
            initial_scale=983,
            initial_north_bias=np.deg2rad(155.6),
        )

        # Load data
        cal.load_data(sample_azalt_coordinates, sample_photo_coordinates)

        # Fit stages
        proj_result = cal.fit_projection()
        assert proj_result["residual_mean"] >= 0

        dist_result = cal.fit_distortion()
        assert "rho" in dist_result and "theta" in dist_result

        # Global fit
        params = cal.global_fit()
        assert params.shape == (23,)

        # Predictions
        predictions = cal.predict(sample_azalt_coordinates)
        assert predictions.shape == sample_photo_coordinates.shape

        # Evaluation
        eval_result = cal.evaluate()
        assert eval_result.rms_error >= 0

        # Parameters
        cal_params = cal.get_calibration_params()
        assert isinstance(cal_params, CalibrationParams)


class TestCalibratorRobustness:
    """Test calibrator robustness to edge cases."""

    def test_single_point(self):
        """Test with single data point."""
        cal = CameraCalibrator()
        azalt = np.array([[0, 45]])
        photo = np.array([[1100, 1100]])

        cal.load_data(azalt, photo)
        # fit_projection should handle single point
        assert cal.polar_azalt.shape == (1, 2)

    def test_duplicate_points(self):
        """Test with duplicate points."""
        cal = CameraCalibrator()
        azalt = np.array([[0, 45], [0, 45], [0, 45]])
        photo = np.array([[1100, 1100], [1100, 1100], [1100, 1100]])

        cal.load_data(azalt, photo)
        assert cal.azalt_data.shape == (3, 2)

    def test_collinear_points(self):
        """Test with collinear points."""
        cal = CameraCalibrator()
        # All points along azimuth=0
        azalt = np.array([[0, 30], [0, 45], [0, 60], [0, 75]])
        photo = np.array([[1053, 1163], [1053, 1220], [1053, 1280], [1053, 1320]])

        cal.load_data(azalt, photo)
        cal.fit_projection()

        assert cal.proj_params is not None
