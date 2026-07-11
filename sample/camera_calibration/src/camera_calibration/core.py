"""
Core camera calibration algorithms.

This module implements the main calibration workflow:
coordinate transformation, projection fitting, and distortion correction.
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Optional, Dict, Any

from .models import (
    CalibrationParams,
    CalibrationResult,
    CoordinateSystemParams,
    ProjectionParams,
    RadialTangentialDistortionParams,
)
from .projections import azalt_to_polar, photo_to_polar, polar_to_photo, polar_to_azalt
from .distortion import (
    rho_projection,
    distortion_term,
    apply_rho_distortion,
    apply_theta_distortion,
)


class CameraCalibrator:
    """
    Main calibrator for camera optical system.

    This class orchestrates the calibration workflow:
    1. Load paired observations (Alt-Az vs photo coordinates)
    2. Convert to polar coordinates
    3. Fit radial projection
    4. Fit radial-tangential distortion
    5. Perform global optimization
    """

    def __init__(
        self,
        initial_center_x: float = 1053.0,
        initial_center_y: float = 1063.0,
        initial_scale: float = 983.0,
        initial_north_bias: float = 2.716,
    ):
        """
        Initialize calibrator with initial estimates.

        Parameters
        ----------
        initial_center_x : float
            Initial estimate of image center X. Units: pixels
        initial_center_y : float
            Initial estimate of image center Y. Units: pixels
        initial_scale : float
            Initial estimate of radial scale factor. Units: pixels
        initial_north_bias : float
            Initial estimate of rotation angle. Units: radians
        """
        self.center_x = initial_center_x
        self.center_y = initial_center_y
        self.scale = initial_scale
        self.north_bias = initial_north_bias

        self.azalt_data: Optional[np.ndarray] = None
        self.photo_data: Optional[np.ndarray] = None
        self.polar_azalt: Optional[np.ndarray] = None
        self.polar_photo: Optional[np.ndarray] = None

        self.proj_params: Optional[np.ndarray] = None
        self.dist_rho_params: Optional[np.ndarray] = None
        self.dist_theta_params: Optional[np.ndarray] = None
        self.full_params: Optional[np.ndarray] = None

    def load_data(self, azalt: np.ndarray, photo: np.ndarray) -> None:
        """
        Load observation data.

        Parameters
        ----------
        azalt : np.ndarray
            Altitude-azimuth coordinates. Shape: (N, 2).
            Columns: [azimuth (deg), altitude (deg)]
        photo : np.ndarray
            Photo pixel coordinates. Shape: (N, 2).
            Columns: [x (pixels), y (pixels)]
        """
        if azalt.shape[0] != photo.shape[0]:
            raise ValueError("azalt and photo must have same number of rows")
        if azalt.shape[1] != 2 or photo.shape[1] != 2:
            raise ValueError("Both arrays must have 2 columns")

        self.azalt_data = azalt.copy()
        self.photo_data = photo.copy()

        # Convert to polar coordinates
        self.polar_azalt = azalt_to_polar(azalt, scale=self.scale, north_bias=self.north_bias)
        self.polar_photo = photo_to_polar(photo, center_x=self.center_x, center_y=self.center_y)

    def fit_projection(self) -> Dict[str, float]:
        """
        Fit radial projection (rho correction).

        Returns
        -------
        dict
            Fit results containing:
            - 'coefficients': Array of 5 projection coefficients
            - 'residual_mean': Mean residual error (pixels)
            - 'residual_max': Maximum residual error (pixels)

        Raises
        ------
        ValueError
            If data not loaded
        """
        if self.polar_azalt is None or self.polar_photo is None:
            raise ValueError("Must load data first with load_data()")

        # Fit polynomial correction
        def projection_func(rho, k0, k1, k2, k3, k4):
            return rho_projection(rho, np.array([k0, k1, k2, k3, k4]))

        popt, _ = curve_fit(
            projection_func, xdata=self.polar_azalt[:, 0], ydata=self.polar_photo[:, 0], maxfev=5000
        )

        self.proj_params = popt

        # Calculate residuals
        predicted_rho = rho_projection(self.polar_azalt[:, 0], self.proj_params)
        residuals = self.polar_photo[:, 0] - predicted_rho

        return {
            "coefficients": self.proj_params,
            "residual_mean": float(np.abs(residuals).mean()),
            "residual_max": float(np.abs(residuals).max()),
        }

    def fit_distortion(self) -> Dict[str, Dict[str, Any]]:
        """
        Fit radial-tangential distortion separately for rho and theta.

        Returns
        -------
        dict
            Results for each coordinate:
            - 'rho': coefficients and residuals
            - 'theta': coefficients and residuals

        Raises
        ------
        ValueError
            If projection not fitted yet
        """
        if self.proj_params is None:
            raise ValueError("Must fit projection first")

        if self.polar_azalt is None:
            raise ValueError("Data not loaded")

        # Create intermediate polar with projection applied
        polar_proj = self.polar_azalt.copy()
        polar_proj[:, 0] = rho_projection(self.polar_azalt[:, 0], self.proj_params)

        # Fit rho distortion
        def distortion_rho_func(polar_flat, r0, r1, r2, t0, t1, t2, t3):
            polar = polar_flat.reshape(-1, 2)
            radial = np.array([r0, r1, r2])
            tangential = np.array([t0, t1, t2, t3])
            return apply_rho_distortion(polar, radial, tangential)

        popt_rho, _ = curve_fit(
            distortion_rho_func,
            xdata=polar_proj.flatten(),
            ydata=self.polar_photo[:, 0],
            maxfev=5000,
        )
        self.dist_rho_params = popt_rho

        # Fit theta distortion
        def distortion_theta_func(polar_flat, r0, r1, r2, t0, t1, t2, t3):
            polar = polar_flat.reshape(-1, 2)
            radial = np.array([r0, r1, r2])
            tangential = np.array([t0, t1, t2, t3])
            return apply_theta_distortion(polar, radial, tangential)

        popt_theta, _ = curve_fit(
            distortion_theta_func,
            xdata=polar_proj.flatten(),
            ydata=self.polar_photo[:, 1],
            maxfev=5000,
        )
        self.dist_theta_params = popt_theta

        # Calculate residuals
        pred_rho = apply_rho_distortion(polar_proj, popt_rho[:3], popt_rho[3:])
        residuals_rho = self.polar_photo[:, 0] - pred_rho

        pred_theta = apply_theta_distortion(polar_proj, popt_theta[:3], popt_theta[3:])
        residuals_theta = self.polar_photo[:, 1] - pred_theta

        return {
            "rho": {
                "coefficients": self.dist_rho_params,
                "residual_mean": float(np.abs(residuals_rho).mean()),
                "residual_max": float(np.abs(residuals_rho).max()),
            },
            "theta": {
                "coefficients": self.dist_theta_params,
                "residual_mean": float(np.abs(residuals_theta).mean()),
                "residual_max": float(np.abs(residuals_theta).max()),
            },
        }

    def global_fit(self) -> np.ndarray:
        """
        Global optimization of all parameters simultaneously.

        Returns
        -------
        np.ndarray
            Optimized parameters [scale, north_bias, proj(5),
            dist_rho(7), dist_theta(7), center_x, center_y]

        Raises
        ------
        ValueError
            If distortion not fitted yet
        """
        if self.dist_rho_params is None or self.dist_theta_params is None:
            raise ValueError("Must fit distortion first")

        if self.azalt_data is None or self.photo_data is None:
            raise ValueError("Data not loaded")

        # Define overall model
        def overall_model(
            azalt_flat,
            scale,
            north_bias,
            k0,
            k1,
            k2,
            k3,
            k4,
            r0,
            r1,
            r2,
            t0,
            t1,
            t2,
            t3,
            r10,
            r11,
            r12,
            t10,
            t11,
            t12,
            t13,
            cx,
            cy,
        ):
            azalt = azalt_flat.reshape(-1, 2)

            # Convert to polar with current parameters
            polar = azalt_to_polar(azalt, scale=scale, north_bias=north_bias)

            # Apply projection
            rho_proj = rho_projection(polar[:, 0], np.array([k0, k1, k2, k3, k4]))
            polar_proj = polar.copy()
            polar_proj[:, 0] = rho_proj

            # Apply distortion
            rho_dist = apply_rho_distortion(
                polar_proj, np.array([r0, r1, r2]), np.array([t0, t1, t2, t3])
            )
            theta_dist = apply_theta_distortion(
                polar_proj, np.array([r10, r11, r12]), np.array([t10, t11, t12, t13])
            )

            # Convert to photo coordinates
            polar_final = np.array([rho_dist, theta_dist]).T
            photo = polar_to_photo(polar_final, center_x=cx, center_y=cy)

            return photo.flatten()

        # Initial parameters
        p0 = [
            self.scale,
            self.north_bias,
            *self.proj_params,
            *self.dist_rho_params,
            *self.dist_theta_params,
            self.center_x,
            self.center_y,
        ]

        popt, _ = curve_fit(
            overall_model,
            xdata=self.azalt_data.flatten(),
            ydata=self.photo_data.flatten(),
            p0=p0,
            maxfev=10000,
        )

        self.full_params = popt
        return popt

    def predict(self, azalt: np.ndarray) -> np.ndarray:
        """
        Predict photo coordinates for given Alt-Az coordinates.

        Parameters
        ----------
        azalt : np.ndarray
            Altitude-azimuth coordinates. Shape: (N, 2). Units: degrees

        Returns
        -------
        np.ndarray
            Predicted photo coordinates. Shape: (N, 2). Units: pixels

        Raises
        ------
        ValueError
            If full model not fitted
        """
        if self.full_params is None:
            raise ValueError("Must perform global_fit first")

        params = self.full_params
        scale, north_bias = params[0:2]
        proj = params[2:7]
        dist_rho = params[7:14]
        dist_theta = params[14:21]
        center_x, center_y = params[21:23]

        # Forward transform
        polar = azalt_to_polar(azalt, scale=scale, north_bias=north_bias)

        # Apply projection
        rho_proj = rho_projection(polar[:, 0], proj)
        polar_proj = polar.copy()
        polar_proj[:, 0] = rho_proj

        # Apply distortion
        rho_dist = apply_rho_distortion(polar_proj, dist_rho[:3], dist_rho[3:])
        theta_dist = apply_theta_distortion(polar_proj, dist_theta[:3], dist_theta[3:])

        # Convert to photo
        polar_final = np.array([rho_dist, theta_dist]).T
        photo = polar_to_photo(polar_final, center_x=center_x, center_y=center_y)

        return photo

    def evaluate(
        self, azalt: Optional[np.ndarray] = None, photo_true: Optional[np.ndarray] = None
    ) -> CalibrationResult:
        """
        Evaluate calibration on test data.

        Parameters
        ----------
        azalt : np.ndarray, optional
            Altitude-azimuth coordinates. If None, uses training data.
        photo_true : np.ndarray, optional
            True photo coordinates. If None, uses training data.

        Returns
        -------
        CalibrationResult
            Evaluation metrics and predictions
        """
        if azalt is None:
            azalt = self.azalt_data
        if photo_true is None:
            photo_true = self.photo_data

        if azalt is None or photo_true is None:
            raise ValueError("No data to evaluate")

        photo_pred = self.predict(azalt)
        error_x = photo_pred[:, 0] - photo_true[:, 0]
        error_y = photo_pred[:, 1] - photo_true[:, 1]

        return CalibrationResult(
            predicted_photo_x=photo_pred[:, 0],
            predicted_photo_y=photo_pred[:, 1],
            error_x=error_x,
            error_y=error_y,
        )

    def get_calibration_params(self) -> CalibrationParams:
        """
        Get complete calibration parameters object.

        Returns
        -------
        CalibrationParams
            Structured calibration parameters

        Raises
        ------
        ValueError
            If full model not fitted
        """
        if self.full_params is None:
            raise ValueError("Must perform global_fit first")

        params = self.full_params

        return CalibrationParams(
            coord_system=CoordinateSystemParams(
                center_x=float(params[21]),
                center_y=float(params[22]),
                scale=float(params[0]),
                north_bias=float(params[1]),
            ),
            projection=ProjectionParams(
                k0=float(params[2]),
                k1=float(params[3]),
                k2=float(params[4]),
                k3=float(params[5]),
                k4=float(params[6]),
            ),
            distortion_rho=RadialTangentialDistortionParams(
                radial0=float(params[7]),
                radial1=float(params[8]),
                radial2=float(params[9]),
                tan0=float(params[10]),
                tan1=float(params[11]),
                tan2=float(params[12]),
                tan3=float(params[13]),
            ),
            distortion_theta=RadialTangentialDistortionParams(
                radial0=float(params[14]),
                radial1=float(params[15]),
                radial2=float(params[16]),
                tan0=float(params[17]),
                tan1=float(params[18]),
                tan2=float(params[19]),
                tan3=float(params[20]),
            ),
        )
