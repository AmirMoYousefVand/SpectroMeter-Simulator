"""
Hardware Kinematic Model for Laboratory Spectrometer-Goniometer.
Manages telescope rotation, clamp mechanics, fine tangent micrometer screw,
and dual Vernier scale readouts with 1-arcminute precision.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

@dataclass
class VernierReading:
    """Decomposition of an angle reading on a 30-arcminute / 1-arcminute Vernier."""
    raw_angle_deg: float
    degrees: int
    msr_arcmin: int       # Main Scale Reading arcminutes (0 or 30)
    vsr_coincident: int   # Vernier Scale Reading line (0 to 29)
    total_arcmin: int
    readout_str: str

    @property
    def decimal_degrees(self) -> float:
        return self.degrees + (self.msr_arcmin + self.vsr_coincident) / 60.0


class SpectrometerModel:
    """
    Physical kinematic state and mechanical controls of the spectrometer.
    """

    def __init__(self):
        # Optical Axes
        self.collimator_angle_deg = 0.0       # Direct path aligns with 0°
        self.central_table_angle_deg = 0.0    # Grating normal orientation
        self.telescope_angle_deg = 0.0        # Continuous arm angle [0, 360)

        # Clamp & Fine Tangent Screw
        self.is_clamped = False
        self.clamp_base_angle_deg = 0.0
        self.fine_tangent_angle_deg = 0.0      # Offset range [-5.0°, +5.0°]

        # Mechanical tolerances & Vernier constants
        self.main_scale_div_deg = 0.5         # 30 arcminutes
        self.vernier_divisions = 30           # 30 lines = 29 main scale lines
        self.least_count_arcmin = 1.0         # 1 arcminute

        # Error offsets
        self.eccentricity_um = 15.0           # 15 micrometers center displacement
        self.eccentricity_phase_deg = 45.0
        self.circle_radius_mm = 85.0          # 85 mm scale radius
        self.enable_eccentricity = True

    # ==========================================================================
    # Telescope Angle & Tangent Mechanics
    # ==========================================================================
    @property
    def effective_telescope_angle(self) -> float:
        """Returns the real physical angle of the telescope in degrees [0, 360)."""
        if self.is_clamped:
            ang = self.clamp_base_angle_deg + self.fine_tangent_angle_deg
        else:
            ang = self.telescope_angle_deg
        return ang % 360.0

    @property
    def deviation_angle(self) -> float:
        """
        Signed deviation angle relative to the direct collimated beam.
        Normalized to [-180.0°, +180.0°]. Positive = Right, Negative = Left.
        """
        diff = self.effective_telescope_angle - self.collimator_angle_deg
        diff = (diff + 180.0) % 360.0 - 180.0
        return diff

    def set_coarse_angle(self, angle_deg: float):
        """Sets coarse telescope angle when unclamped."""
        if not self.is_clamped:
            self.telescope_angle_deg = float(angle_deg) % 360.0

    def set_fine_tangent(self, offset_deg: float):
        """Sets fine tangent micrometer screw displacement when clamped."""
        if self.is_clamped:
            self.fine_tangent_angle_deg = float(max(-5.0, min(5.0, offset_deg)))

    def toggle_clamp(self) -> bool:
        """Toggles locking clamp screw on the telescope arm."""
        if not self.is_clamped:
            # Locking: freeze current position as clamp base, reset fine screw
            self.clamp_base_angle_deg = self.telescope_angle_deg
            self.fine_tangent_angle_deg = 0.0
            self.is_clamped = True
        else:
            # Unlocking: transfer clamped position to free telescope angle
            self.telescope_angle_deg = self.effective_telescope_angle
            self.fine_tangent_angle_deg = 0.0
            self.is_clamped = False
        return self.is_clamped

    # ==========================================================================
    # Vernier Reading Synthesis
    # ==========================================================================
    def get_vernier_readings(self) -> Tuple[VernierReading, VernierReading]:
        """
        Computes accurate readings for Vernier 1 and Vernier 2 (180° opposite).
        Applies mechanical eccentricity error if enabled.
        """
        theta = self.effective_telescope_angle

        # Mechanical eccentricity perturbation: δθ = (e / R) * sin(θ - φ0)
        if self.enable_eccentricity:
            # e in mm = um * 1e-3
            e_mm = self.eccentricity_um * 1e-3
            delta_rad = (e_mm / self.circle_radius_mm) * math.sin(math.radians(theta - self.eccentricity_phase_deg))
            delta_deg = math.degrees(delta_rad)
        else:
            delta_deg = 0.0

        v1_angle = (theta + delta_deg) % 360.0
        v2_angle = (theta + 180.0 - delta_deg) % 360.0

        v1_decomp = self.decompose_angle_to_vernier(v1_angle)
        v2_decomp = self.decompose_angle_to_vernier(v2_angle)

        return v1_decomp, v2_decomp

    @staticmethod
    def decompose_angle_to_vernier(angle_deg: float) -> VernierReading:
        """
        Decomposes decimal degrees into:
        - Whole Degrees (0 to 359)
        - Main Scale Minutes (0' or 30')
        - Vernier Coincident Mark (0' to 29')
        Least count = 1 arcminute.
        """
        ang = float(angle_deg) % 360.0
        total_minutes = int(round(ang * 60.0))
        total_minutes = total_minutes % (360 * 60)

        degrees = total_minutes // 60
        rem_min = total_minutes % 60

        msr_arcmin = (rem_min // 30) * 30       # 0 or 30 arcminutes
        vsr_coincident = rem_min % 30           # 0 to 29 arcminutes

        readout_str = f"{degrees}° {msr_arcmin + vsr_coincident:02d}'"

        return VernierReading(
            raw_angle_deg=ang,
            degrees=degrees,
            msr_arcmin=msr_arcmin,
            vsr_coincident=vsr_coincident,
            total_arcmin=msr_arcmin + vsr_coincident,
            readout_str=readout_str
        )

    def get_corrected_angle_from_verniers(self, v1: VernierReading, v2: VernierReading) -> float:
        """
        Calculates eccentricity-corrected angle by circular averaging V1 and (V2 - 180°):
        θ_corr = V1 + circular_diff(V2 - 180°, V1) / 2
        Correctly handles wrap-around near 0° / 360°.
        """
        v1_val = v1.decimal_degrees % 360.0
        v2_val = (v2.decimal_degrees - 180.0) % 360.0
        diff = (v2_val - v1_val + 180.0) % 360.0 - 180.0
        return (v1_val + diff / 2.0) % 360.0
