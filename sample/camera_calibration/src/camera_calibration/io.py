"""
I/O operations for camera calibration data.

This module handles loading and saving calibration data and results.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import numpy as np
import pandas as pd

from .models import CalibrationParams, CalibrationResult


class CalibrationIO:
    """Handler for loading and saving calibration data."""

    @staticmethod
    def load_observation_data(csv_path: str) -> tuple:
        """
        Load observation data from CSV file.

        Expected CSV format:
        az, alt, extracted_x, extracted_y

        Parameters
        ----------
        csv_path : str
            Path to CSV file containing [az, alt, extracted_x, extracted_y] columns

        Returns
        -------
        tuple
            (azalt, photo) where each is np.ndarray of shape (N, 2)
            azalt columns: [azimuth (deg), altitude (deg)]
            photo columns: [x (pixels), y (pixels)]

        Raises
        ------
        FileNotFoundError
            If file does not exist
        ValueError
            If CSV does not have required columns
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Data file not found: {csv_path}")

        df = pd.read_csv(csv_path)

        # Check required columns
        required = ["az", "alt", "extracted_x", "extracted_y"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")

        azalt = df[["az", "alt"]].values
        photo = df[["extracted_x", "extracted_y"]].values

        return azalt, photo

    @staticmethod
    def save_calibration_params(params: CalibrationParams, output_path: str) -> None:
        """
        Save calibration parameters to JSON file.

        Parameters
        ----------
        params : CalibrationParams
            Calibration parameters to save
        output_path : str
            Path where to save the parameters
        """
        data = {
            "coordinate_system": {
                "center_x": float(params.coord_system.center_x),
                "center_y": float(params.coord_system.center_y),
                "scale": float(params.coord_system.scale),
                "north_bias": float(params.coord_system.north_bias),
            },
            "projection": {
                "k0": float(params.projection.k0),
                "k1": float(params.projection.k1),
                "k2": float(params.projection.k2),
                "k3": float(params.projection.k3),
                "k4": float(params.projection.k4),
            },
            "distortion_rho": {
                "radial0": float(params.distortion_rho.radial0),
                "radial1": float(params.distortion_rho.radial1),
                "radial2": float(params.distortion_rho.radial2),
                "tan0": float(params.distortion_rho.tan0),
                "tan1": float(params.distortion_rho.tan1),
                "tan2": float(params.distortion_rho.tan2),
                "tan3": float(params.distortion_rho.tan3),
            },
            "distortion_theta": {
                "radial0": float(params.distortion_theta.radial0),
                "radial1": float(params.distortion_theta.radial1),
                "radial2": float(params.distortion_theta.radial2),
                "tan0": float(params.distortion_theta.tan0),
                "tan1": float(params.distortion_theta.tan1),
                "tan2": float(params.distortion_theta.tan2),
                "tan3": float(params.distortion_theta.tan3),
            },
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_calibration_params(json_path: str) -> CalibrationParams:
        """
        Load calibration parameters from JSON file.

        Parameters
        ----------
        json_path : str
            Path to JSON file containing calibration parameters

        Returns
        -------
        CalibrationParams
            Loaded calibration parameters

        Raises
        ------
        FileNotFoundError
            If file does not exist
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Parameters file not found: {json_path}")

        with open(json_path, "r") as f:
            data = json.load(f)

        from .models import (
            CoordinateSystemParams,
            ProjectionParams,
            RadialTangentialDistortionParams,
        )

        return CalibrationParams(
            coord_system=CoordinateSystemParams(**data["coordinate_system"]),
            projection=ProjectionParams(**data["projection"]),
            distortion_rho=RadialTangentialDistortionParams(**data["distortion_rho"]),
            distortion_theta=RadialTangentialDistortionParams(**data["distortion_theta"]),
        )

    @staticmethod
    def save_result(
        result: CalibrationResult,
        output_csv: str,
        azalt_original: Optional[np.ndarray] = None,
        polar_photo: Optional[np.ndarray] = None,
        polar_predicted: Optional[np.ndarray] = None,
    ) -> None:
        """
        Save calibration results to CSV file.

        Parameters
        ----------
        result : CalibrationResult
            Calibration result containing predictions and errors
        output_csv : str
            Output CSV file path
        azalt_original : np.ndarray, optional
            Original Alt-Az coordinates for reference
        polar_photo : np.ndarray, optional
            Original photo coordinates in polar form
        polar_predicted : np.ndarray, optional
            Predicted coordinates in polar form
        """
        df = pd.DataFrame(
            {
                "predicted_x": result.predicted_photo_x,
                "predicted_y": result.predicted_photo_y,
                "error_x": result.error_x,
                "error_y": result.error_y,
                "error_rms": np.sqrt(result.error_x**2 + result.error_y**2),
            }
        )

        if azalt_original is not None:
            df["azimuth"] = azalt_original[:, 0]
            df["altitude"] = azalt_original[:, 1]

        if polar_photo is not None:
            df["photo_rho"] = polar_photo[:, 0]
            df["photo_theta"] = polar_photo[:, 1]

        if polar_predicted is not None:
            df["predicted_rho"] = polar_predicted[:, 0]
            df["predicted_theta"] = polar_predicted[:, 1]

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False)

    @staticmethod
    def save_evaluation_summary(result: CalibrationResult, output_json: str) -> None:
        """
        Save evaluation summary metrics.

        Parameters
        ----------
        result : CalibrationResult
            Evaluation result
        output_json : str
            Output JSON file path
        """
        summary = {
            "rms_error_pixels": float(result.rms_error),
            "max_error_pixels": float(result.max_error),
            "mean_error_x": float(np.mean(np.abs(result.error_x))),
            "mean_error_y": float(np.mean(np.abs(result.error_y))),
            "std_error_x": float(np.std(result.error_x)),
            "std_error_y": float(np.std(result.error_y)),
            "n_points": int(len(result.error_x)),
        }

        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w") as f:
            json.dump(summary, f, indent=2)
