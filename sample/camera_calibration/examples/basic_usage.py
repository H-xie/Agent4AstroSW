"""
Basic usage example of the camera_calibration package.

This script demonstrates the main workflow:
1. Load paired observations (Alt-Az vs photo coordinates)
2. Perform camera calibration
3. Generate calibration results
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path for direct import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from camera_calibration.core import CameraCalibrator
from camera_calibration.models import CalibrationParams


def generate_synthetic_data(n_points: int = 50) -> tuple:
    """
    Generate synthetic calibration data for demonstration.

    Returns
    -------
    azalt : np.ndarray
        Synthetic Alt-Az coordinates (N, 2)
    photo : np.ndarray
        Synthetic photo coordinates (N, 2)
    """
    np.random.seed(42)

    # Generate random Alt-Az coordinates
    azimuths = np.random.uniform(0, 360, n_points)
    altitudes = np.random.uniform(20, 85, n_points)
    azalt = np.column_stack([azimuths, altitudes])

    # Generate synthetic photo coordinates using a simple forward model
    # (In real applications, these would be measured from actual images)
    from camera_calibration.projections import azalt_to_polar, polar_to_photo

    center_x, center_y = 1053.0, 1063.0
    scale = 983.0
    north_bias = 2.716

    # Convert to polar
    polar = azalt_to_polar(azalt, scale=scale, north_bias=north_bias)

    # Apply small distortion
    polar[:, 0] *= 1 + 0.001 * np.sin(polar[:, 1])  # Simple radial distortion

    # Convert back to photo
    photo = polar_to_photo(polar, center_x=center_x, center_y=center_y)

    # Add small noise
    photo += np.random.normal(0, 0.5, photo.shape)

    return azalt, photo


def main():
    """Run basic calibration example."""
    print("=" * 60)
    print("Camera Calibration Package - Basic Usage Example")
    print("=" * 60)

    # Step 1: Generate synthetic data
    print("\n1. Generating synthetic calibration data...")
    azalt, photo = generate_synthetic_data(n_points=50)
    print(f"   Generated {len(azalt)} calibration points")
    print(
        f"   Alt-Az range: Az=[{azalt[:, 0].min():.1f}, {azalt[:, 0].max():.1f}]°, "
        f"Alt=[{azalt[:, 1].min():.1f}, {azalt[:, 1].max():.1f}]°"
    )
    print(
        f"   Photo range: X=[{photo[:, 0].min():.1f}, {photo[:, 0].max():.1f}], "
        f"Y=[{photo[:, 1].min():.1f}, {photo[:, 1].max():.1f}]"
    )

    # Step 2: Initialize calibrator
    print("\n2. Initializing Camera Calibrator...")
    calibrator = CameraCalibrator(
        initial_center_x=1053.0,
        initial_center_y=1063.0,
        initial_scale=983.0,
        initial_north_bias=2.716,
    )
    print(f"   Initial center: ({calibrator.center_x}, {calibrator.center_y})")
    print(f"   Initial scale: {calibrator.scale} pixels")
    print(f"   Initial north bias: {calibrator.north_bias:.3f} rad")

    # Step 3: Load data
    print("\n3. Loading observation data...")
    calibrator.load_data(azalt, photo)
    print(
        f"   Data loaded: {calibrator.azalt_data.shape} Alt-Az pairs, "
        f"{calibrator.photo_data.shape} photo pairs"
    )

    # Step 4: Perform calibration steps
    print("\n4. Performing calibration steps...")

    try:
        # Step 4a: Fit projection
        print("   4a. Fitting radial projection...")
        calibrator.fit_projection()
        if calibrator.proj_params is not None:
            print(f"      ✓ Projection parameters fitted (5 coefficients)")

        # Step 4b: Fit distortion
        print("   4b. Fitting radial-tangential distortion...")
        calibrator.fit_distortion()
        if calibrator.dist_rho_params is not None:
            print(f"      ✓ Radial-tangential distortion parameters fitted")

        # Step 4c: Global optimization
        print("   4c. Performing global optimization...")
        result = calibrator.fit_global()
        if result is not None:
            print(f"      ✓ Global fit completed")
            print(f"      - Center: ({result.center_x:.2f}, {result.center_y:.2f})")
            print(f"      - Scale: {result.scale:.2f} pixels")
            print(f"      - North bias: {result.north_bias:.4f} rad")
            print(f"      - RMS error: {result.rms_error:.3f} pixels")

    except Exception as e:
        print(f"   ✗ Error during calibration: {e}")
        return

    # Step 5: Validation
    print("\n5. Validation...")
    if calibrator.full_params is not None:
        # Generate predictions
        from camera_calibration.core import CameraCalibrator

        pred_photo = calibrator.predict(azalt)
        errors = photo - pred_photo
        error_rms = np.sqrt((errors**2).sum(axis=1)).mean()
        print(f"   Prediction RMS error: {error_rms:.3f} pixels")
        print(f"   Max error: {np.sqrt((errors ** 2).sum(axis=1)).max():.3f} pixels")
        print(
            f"   Mean absolute error: X={np.abs(errors[:, 0]).mean():.3f}, "
            f"Y={np.abs(errors[:, 1]).mean():.3f}"
        )

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
