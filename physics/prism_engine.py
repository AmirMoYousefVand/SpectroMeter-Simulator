"""
Prism Optics & Cauchy Dispersion Engine (موتور فیزیک پاشندگی منشور شیشه‌ای).
Simulates double refraction through an equilateral prism (A = 60°),
Cauchy dispersion relation n(λ) = A + B/λ², angle of minimum deviation (D_min),
and angular separation where violet refracts more than red.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from physics.constants import SpectralLine, SpectralSource
from utils.color_utils import ColorUtils

@dataclass
class RefractedPeak:
    """Calculated position and properties of a spectral line refracted through a prism."""
    line_name: str
    wavelength_nm: float
    angle_deg: float          # Deviation angle relative to direct beam
    refractive_index_n: float
    intensity: float
    color_hint: str
    order_m: int = 1
    is_missing_order: bool = False
    transition: Optional[str] = None
    n_upper: Optional[int] = None


class PrismEngine:
    """
    Physical calculations for triangular glass prism dispersion.
    """

    def __init__(
        self,
        apex_angle_deg: float = 60.0,
        glass_type: str = "Dense Flint",
        cauchy_A: float = 1.620,
        cauchy_B_nm2: float = 12500.0,  # B in nm^2 (1.25e-14 m^2 = 1.25e4 nm^2)
        base_incidence_deg: Optional[float] = None
    ):
        self.apex_angle_deg = float(apex_angle_deg)
        self.glass_type = glass_type
        self.cauchy_A = float(cauchy_A)
        self.cauchy_B_nm2 = float(cauchy_B_nm2)
        self.base_incidence_deg = base_incidence_deg

    def get_refractive_index(self, wavelength_nm: float) -> float:
        """
        Computes refractive index using Cauchy's empirical equation:
        n(λ) = A + B / λ²
        """
        wl = max(300.0, float(wavelength_nm))
        n = self.cauchy_A + (self.cauchy_B_nm2 / (wl ** 2))
        return float(n)

    def calculate_minimum_deviation_deg(self, wavelength_nm: float) -> float:
        """
        Calculates angle of minimum deviation D_min where i1 = i2 = (A + D_min)/2:
        n = sin((A + D_min)/2) / sin(A/2)
        ==> D_min = 2 * arcsin(n * sin(A/2)) - A
        """
        n = self.get_refractive_index(wavelength_nm)
        a_half_rad = math.radians(self.apex_angle_deg / 2.0)
        sin_val = n * math.sin(a_half_rad)

        if abs(sin_val) > 1.0:
            sin_val = 1.0

        i_min_rad = math.asin(sin_val)
        d_min_deg = math.degrees(2.0 * i_min_rad) - self.apex_angle_deg
        return float(d_min_deg)

    def calculate_deviation_deg(self, wavelength_nm: float, incidence_deg: Optional[float] = None) -> Optional[float]:
        """
        Calculates total deviation angle δ = i1 + i2 - A through prism.
        If incidence angle is None, evaluates at symmetrical minimum deviation condition.
        """
        if incidence_deg is None:
            return self.calculate_minimum_deviation_deg(wavelength_nm)

        n = self.get_refractive_index(wavelength_nm)
        i1_rad = math.radians(incidence_deg)

        # First surface: sin i1 = n * sin r1
        sin_r1 = math.sin(i1_rad) / n
        if abs(sin_r1) > 1.0:
            return None # Total internal reflection on face 1
        r1_rad = math.asin(sin_r1)

        # Second surface: r2 = A - r1
        a_rad = math.radians(self.apex_angle_deg)
        r2_rad = a_rad - r1_rad
        if r2_rad < 0:
            return None

        # Refraction out of face 2: n * sin r2 = sin i2
        sin_i2 = n * math.sin(r2_rad)
        if abs(sin_i2) > 1.0:
            return None # Total internal reflection on face 2

        i2_rad = math.asin(sin_i2)
        dev_rad = i1_rad + i2_rad - a_rad
        return float(math.degrees(dev_rad))

    def compute_all_peaks(self, source: SpectralSource) -> List[RefractedPeak]:
        """
        Computes refracted line positions for the selected spectral source.
        Violet light (shorter wavelength) has higher n and refracts at a LARGER deviation angle than red!
        """
        peaks: List[RefractedPeak] = []

        lines = source.lines
        if source.is_continuous:
            lines = [
                SpectralLine("Violet Edge", 400.0, 0.7, "#8A2BE2"),
                SpectralLine("Blue",        450.0, 0.8, "#1E90FF"),
                SpectralLine("Cyan",        500.0, 0.9, "#00E5EE"),
                SpectralLine("Green",       550.0, 1.0, "#00FF00"),
                SpectralLine("Yellow",      590.0, 0.95, "#FFD700"),
                SpectralLine("Orange",      630.0, 0.85, "#FF8C00"),
                SpectralLine("Red Edge",    700.0, 0.75, "#FF0000"),
            ]

        for line in lines:
            dev_deg = self.calculate_deviation_deg(line.wavelength_nm, self.base_incidence_deg)
            if dev_deg is None:
                continue
            n_val = self.get_refractive_index(line.wavelength_nm)
            hex_col = line.color_hint or ColorUtils.wavelength_to_hex(line.wavelength_nm)

            peaks.append(RefractedPeak(
                line_name=line.name,
                wavelength_nm=line.wavelength_nm,
                angle_deg=dev_deg,
                refractive_index_n=n_val,
                intensity=line.intensity,
                color_hint=hex_col,
                transition=line.transition,
                n_upper=line.n_upper
            ))

        # Sort peaks by deviation angle
        peaks.sort(key=lambda p: p.angle_deg)
        return peaks

    def compute_spectrum_profile_1d(
        self,
        source: SpectralSource,
        theta_grid_deg: np.ndarray,
        focus_blur_factor: float = 1.0
    ) -> Tuple[np.ndarray, List[RefractedPeak]]:
        """
        Synthesizes 1D spectral intensity curve for prism dispersion.
        """
        intensity = np.zeros_like(theta_grid_deg, dtype=float)
        peaks = self.compute_all_peaks(source)

        line_sigma_deg = 0.18 * max(0.5, focus_blur_factor)
        two_sigma_sq = 2.0 * (line_sigma_deg ** 2)

        for p in peaks:
            delta_theta = theta_grid_deg - p.angle_deg
            mask = np.abs(delta_theta) < (4.0 * line_sigma_deg)
            if np.any(mask):
                intensity[mask] += p.intensity * np.exp(-(delta_theta[mask] ** 2) / two_sigma_sq)

        intensity = np.clip(intensity, 0.0, None)
        max_val = np.max(intensity) if len(intensity) > 0 else 1.0
        if max_val > 1e-12:
            intensity /= max_val

        return intensity, peaks
