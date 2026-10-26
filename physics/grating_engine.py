"""
Diffraction Grating Physics Engine.
Computes Fraunhofer diffraction angles, Fraunhofer/N-slit intensity distributions,
Rayleigh resolving power, angular dispersion, and missing orders.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from physics.constants import SpectralLine, SpectralSource, RYDBERG_CONSTANT_H

@dataclass
class DiffractedPeak:
    """Calculated physical position and intensity of a diffracted spectral line."""
    line_name: str
    wavelength_nm: float
    order_m: int
    angle_deg: float         # Deflection angle relative to direct beam
    intensity: float         # Normalized [0.0, 1.0]
    color_hint: str
    angular_dispersion_deg_per_nm: float
    resolving_power_R: float
    min_resolvable_dlambda_nm: float
    is_missing_order: bool = False
    transition: Optional[str] = None
    n_upper: Optional[int] = None


class GratingEngine:
    """
    Physical calculation engine for diffraction gratings.
    """

    def __init__(
        self,
        lines_per_mm: float = 600.0,
        slit_width_mm: float = 0.05,
        beam_width_mm: float = 15.0,
        oblique_incidence_deg: float = 0.0
    ):
        self.lines_per_mm = max(10.0, float(lines_per_mm))
        self.slit_width_mm = max(0.005, float(slit_width_mm))
        self.beam_width_mm = max(1.0, float(beam_width_mm))
        self.oblique_incidence_deg = float(oblique_incidence_deg)

    @property
    def d_m(self) -> float:
        """Grating constant (groove spacing) in meters."""
        return 1.0 / (self.lines_per_mm * 1e3)

    @property
    def d_nm(self) -> float:
        """Grating constant in nanometers."""
        return self.d_m * 1e9

    @property
    def slit_width_m(self) -> float:
        """Entrance slit width in meters."""
        return self.slit_width_mm * 1e-3

    @property
    def illuminated_lines_Nt(self) -> float:
        """Total number of illuminated grating grooves."""
        return (self.beam_width_mm * 1e-3) / self.d_m

    # ==========================================================================
    # Grating Equation & Peak Calculations
    # ==========================================================================
    def calculate_diffraction_angle_deg(self, wavelength_nm: float, order_m: int) -> Optional[float]:
        """
        Calculates diffraction angle theta_m using:
        sin(theta_m) = sin(theta_i) + m * lambda / d
        Returns angle in degrees [-90°, +90°], or None if evanescent / beyond 90°.
        """
        wl_m = wavelength_nm * 1e-9
        theta_i_rad = math.radians(self.oblique_incidence_deg)

        sin_val = math.sin(theta_i_rad) + (order_m * wl_m) / self.d_m

        if abs(sin_val) > 1.0:
            return None

        theta_m_rad = math.asin(sin_val)
        return math.degrees(theta_m_rad)

    def check_missing_order(self, order_m: int) -> bool:
        """
        Checks if diffraction order coincides with single-slit diffraction minimum:
        m / p = d / a
        """
        if order_m == 0:
            return False
        ratio = self.d_m / self.slit_width_m
        if ratio <= 0:
            return False
        nearest_ratio = round(ratio)
        if nearest_ratio >= 1 and abs(ratio - nearest_ratio) < 0.08:
            if order_m % nearest_ratio == 0:
                return True
        return False

    def compute_all_peaks(self, source: SpectralSource, max_order: int = 3) -> List[DiffractedPeak]:
        """
        Computes all diffracted spectral peaks visible for a given light source.
        Includes order m = 0 and m = +/-1, +/-2, ..., +/-max_order.
        """
        peaks: List[DiffractedPeak] = []
        theta_i_rad = math.radians(self.oblique_incidence_deg)

        # 1. Zero Order (m = 0): Central transmission of all wavelengths
        zero_angle_deg = math.degrees(theta_i_rad)
        if source.is_continuous:
            # White light central fringe
            peaks.append(DiffractedPeak(
                line_name="Central White",
                wavelength_nm=550.0,
                order_m=0,
                angle_deg=zero_angle_deg,
                intensity=1.0,
                color_hint="#FFFFFF",
                angular_dispersion_deg_per_nm=0.0,
                resolving_power_R=0.0,
                min_resolvable_dlambda_nm=0.0,
                is_missing_order=False
            ))
        else:
            for line in source.lines:
                peaks.append(DiffractedPeak(
                    line_name=f"{line.name} (m=0)",
                    wavelength_nm=line.wavelength_nm,
                    order_m=0,
                    angle_deg=zero_angle_deg,
                    intensity=line.intensity,
                    color_hint=line.color_hint or "#FFFFFF",
                    angular_dispersion_deg_per_nm=0.0,
                    resolving_power_R=0.0,
                    min_resolvable_dlambda_nm=0.0,
                    is_missing_order=False,
                    transition=line.transition,
                    n_upper=line.n_upper
                ))

        # 2. Non-zero orders (m = +1, -1, +2, -2, ...)
        orders = []
        for m in range(1, max_order + 1):
            orders.extend([m, -m])

        lines_to_eval = source.lines
        if source.is_continuous:
            # Sample discrete spectral markers for white light
            lines_to_eval = [
                SpectralLine("Violet Edge", 400.0, 0.7, "#8A2BE2"),
                SpectralLine("Blue",        450.0, 0.8, "#1E90FF"),
                SpectralLine("Cyan",        500.0, 0.9, "#00E5EE"),
                SpectralLine("Green",       550.0, 1.0, "#00FF00"),
                SpectralLine("Yellow",      590.0, 0.95, "#FFD700"),
                SpectralLine("Orange",      630.0, 0.85, "#FF8C00"),
                SpectralLine("Red Edge",    700.0, 0.75, "#FF0000"),
            ]

        for order in orders:
            for line in lines_to_eval:
                ang_deg = self.calculate_diffraction_angle_deg(line.wavelength_nm, order)
                if ang_deg is None:
                    continue

                ang_rad = math.radians(ang_deg)
                cos_ang = math.cos(ang_rad)

                # Angular dispersion D = m / (d * cos θ) in rad/m -> deg/nm
                if cos_ang > 1e-6:
                    d_rad_per_m = abs(order) / (self.d_m * cos_ang)
                    d_deg_per_nm = math.degrees(d_rad_per_m) * 1e-9
                else:
                    d_deg_per_nm = 0.0

                # Resolving power R = |m| * N_t
                r_power = abs(order) * self.illuminated_lines_Nt
                min_dlambda = line.wavelength_nm / r_power if r_power > 0 else 0.0

                # Single slit diffraction envelope factor [sin(beta)/beta]^2
                beta = (math.pi * self.slit_width_m / (line.wavelength_nm * 1e-9)) * (math.sin(ang_rad) - math.sin(theta_i_rad))
                sinc_beta = math.sin(beta) / beta if abs(beta) > 1e-7 else 1.0
                envelope = sinc_beta * sinc_beta

                is_missing = self.check_missing_order(order)
                eff_intensity = 0.0 if is_missing else float(np.clip(line.intensity * envelope, 0.01, 1.0))

                peaks.append(DiffractedPeak(
                    line_name=line.name,
                    wavelength_nm=line.wavelength_nm,
                    order_m=order,
                    angle_deg=ang_deg,
                    intensity=eff_intensity,
                    color_hint=line.color_hint or "#FFFF00",
                    angular_dispersion_deg_per_nm=d_deg_per_nm,
                    resolving_power_R=r_power,
                    min_resolvable_dlambda_nm=min_dlambda,
                    is_missing_order=is_missing,
                    transition=line.transition,
                    n_upper=line.n_upper
                ))

        # Sort peaks by angle
        peaks.sort(key=lambda p: p.angle_deg)
        return peaks

    # ==========================================================================
    # Fast Intensity Spectrum Synthesis
    # ==========================================================================
    def compute_spectrum_profile_1d(
        self,
        source: SpectralSource,
        theta_grid_deg: np.ndarray,
        focus_blur_factor: float = 1.0
    ) -> Tuple[np.ndarray, List[DiffractedPeak]]:
        """
        Synthesizes 1D spectral intensity array across theta_grid_deg.
        Applies line profile model convolved with focus blur.
        """
        intensity = np.zeros_like(theta_grid_deg, dtype=float)
        peaks = self.compute_all_peaks(source, max_order=3)

        # Base diffraction-limited line angular half-width
        base_hwhm_deg = math.degrees(0.5 / (self.illuminated_lines_Nt if self.illuminated_lines_Nt > 0 else 1000.0))
        # Entrance slit geometric width
        slit_geom_deg = math.degrees(self.slit_width_m / 0.178) # f_coll = 178mm
        # Combined line width
        line_sigma_deg = math.sqrt(base_hwhm_deg**2 + (0.5 * slit_geom_deg)**2) * max(0.5, focus_blur_factor)

        two_sigma_sq = 2.0 * (line_sigma_deg ** 2)

        for p in peaks:
            if p.is_missing_order or p.intensity <= 0:
                continue

            # Gaussian line profile centered at p.angle_deg
            delta_theta = theta_grid_deg - p.angle_deg
            # Optimization: evaluate only within +/- 4 sigma
            mask = np.abs(delta_theta) < (4.0 * line_sigma_deg)
            if np.any(mask):
                intensity[mask] += p.intensity * np.exp(-(delta_theta[mask] ** 2) / two_sigma_sq)

        # Baseline dark background
        intensity = np.clip(intensity, 0.0, None)
        max_val = np.max(intensity) if len(intensity) > 0 else 1.0
        if max_val > 1e-12:
            intensity /= max_val

        return intensity, peaks

    # ==========================================================================
    # Rydberg Constant Extractor (for Hydrogen)
    # ==========================================================================
    @staticmethod
    def calculate_rydberg_constant(measured_angle_deg: float, order_m: int, d_m: float, n_upper: int) -> Dict[str, float]:
        """
        Calculates experimental Rydberg constant from Balmer line:
        1 / lambda = R_H * (1/4 - 1/n^2)
        """
        if order_m == 0 or n_upper <= 2:
            return {"R_H_exp": 0.0, "rel_error_percent": 100.0, "lambda_calc_nm": 0.0}

        theta_rad = math.radians(abs(measured_angle_deg))
        sin_theta = math.sin(theta_rad)
        if sin_theta <= 1e-6:
            return {"R_H_exp": 0.0, "rel_error_percent": 100.0, "lambda_calc_nm": 0.0}

        lambda_calc_m = (d_m * sin_theta) / abs(order_m)
        balmer_factor = 0.25 - (1.0 / (n_upper ** 2))

        if balmer_factor <= 0:
            return {"R_H_exp": 0.0, "rel_error_percent": 100.0, "lambda_calc_nm": lambda_calc_m * 1e9}

        r_h_exp = 1.0 / (lambda_calc_m * balmer_factor)
        rel_error = abs(r_h_exp - RYDBERG_CONSTANT_H) / RYDBERG_CONSTANT_H * 100.0

        return {
            "R_H_exp": r_h_exp,
            "R_H_true": RYDBERG_CONSTANT_H,
            "rel_error_percent": rel_error,
            "lambda_calc_nm": lambda_calc_m * 1e9
        }
