"""
Physical Error Simulation Engine for Laboratory Spectrometer.
Models optical defocus blur (PSF), grating table leveling tilt (Schuster method),
oblique incidence asymmetry, and mechanical Vernier eccentricity error.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class ErrorParameters:
    """Configuration container for systematic laboratory errors."""
    enabled: bool = True
    collimator_focus_percent: float = 50.0   # 50% = perfectly focused
    telescope_focus_percent: float = 50.0    # 50% = perfectly focused
    table_tilt_x_deg: float = 0.0            # Pitch tilt of grating table
    table_tilt_y_deg: float = 0.0            # Roll tilt of grating table
    oblique_incidence_deg: float = 0.0       # Non-normal collimator alignment
    eccentricity_um: float = 15.0            # Axis offset (micrometers)
    eccentricity_phase_deg: float = 45.0     # Phase angle of eccentricity vector


class SpectrometerErrorModel:
    """
    Evaluates realistic physical aberrations and alignment errors.
    """

    def __init__(self, params: ErrorParameters = None):
        self.params = params or ErrorParameters()

    def get_focus_blur_factor(self) -> float:
        """
        Calculates line broadening factor based on collimator and telescope focus.
        1.0 = sharp diffraction-limited lines.
        Values up to 8.0 = severely blurred, overlapping lines.
        """
        if not self.params.enabled:
            return 1.0

        # Deviation from ideal 50%
        df_coll = abs(self.params.collimator_focus_percent - 50.0) / 50.0
        df_tele = abs(self.params.telescope_focus_percent - 50.0) / 50.0

        total_defocus = (df_coll * 1.5) + (df_tele * 2.0)
        # Non-linear quadratic growth of Point Spread Function
        blur_factor = 1.0 + (total_defocus ** 1.8) * 6.0
        return float(blur_factor)

    def get_grating_tilt_offsets(self, telescope_angle_deg: float) -> Tuple[float, float]:
        """
        Calculates vertical reticle drift and slit tilt angle induced by
        unlevel grating table (Schuster method alignment).
        Returns:
            (vertical_drift_norm, slit_slant_deg)
            vertical_drift_norm: offset in [-1.0, 1.0] relative to FOV radius
            slit_slant_deg: rotation of vertical slit in degrees [-15°, +15°]
        """
        if not self.params.enabled:
            return 0.0, 0.0

        theta_rad = math.radians(telescope_angle_deg)
        tilt_x_rad = math.radians(self.params.table_tilt_x_deg)
        tilt_y_rad = math.radians(self.params.table_tilt_y_deg)

        # Vertical image drift on reticle: y_drift ~ (tilt_x * sin θ - tilt_y * cos θ)
        y_drift_rad = tilt_x_rad * math.sin(theta_rad) - tilt_y_rad * math.cos(theta_rad)
        # Scaled to eyepiece 3.0° FOV: drift_norm = drift_deg / 1.5°
        drift_norm = math.degrees(y_drift_rad) / 1.5

        # Slit image slant / tilt angle on reticle
        slant_rad = tilt_x_rad * math.cos(theta_rad) + tilt_y_rad * math.sin(theta_rad)
        slant_deg = math.degrees(slant_rad) * 4.0 # Visual exaggeration factor for feedback

        return float(drift_norm), float(slant_deg)

    def get_eccentricity_delta_deg(self, telescope_angle_deg: float, circle_radius_mm: float = 85.0) -> float:
        """
        Calculates angular discrepancy between pivot axis and graduated circle:
        δθ = (e / R) * sin(θ - φ0)
        """
        if not self.params.enabled or self.params.eccentricity_um <= 0:
            return 0.0

        e_mm = self.params.eccentricity_um * 1e-3
        theta_eff = math.radians(telescope_angle_deg - self.params.eccentricity_phase_deg)
        delta_rad = (e_mm / circle_radius_mm) * math.sin(theta_eff)
        return math.degrees(delta_rad)
