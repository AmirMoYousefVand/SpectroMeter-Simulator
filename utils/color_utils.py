"""
Color Utilities for Wavelength-to-sRGB Spectral Mapping,
Continuous Spectrum Strips, and Optical Glow/Bloom Rendering.
"""

from typing import Tuple, List, Optional
import numpy as np

class ColorUtils:
    """
    Implements physical wavelength-to-sRGB mapping based on Dan Bruton's
    CIE colorimetric algorithm with eye photopic sensitivity correction.
    """

    @staticmethod
    def wavelength_to_rgb(wavelength_nm: float, gamma: float = 0.8) -> Tuple[int, int, int]:
        """
        Converts visible wavelength (380 to 780 nm) into sRGB integer values (0 to 255).
        """
        wl = float(wavelength_nm)

        # 1. Base RGB Spectral Interpolation
        if 380.0 <= wl < 440.0:
            r = -(wl - 440.0) / (440.0 - 380.0)
            g = 0.0
            b = 1.0
        elif 440.0 <= wl < 490.0:
            r = 0.0
            g = (wl - 440.0) / (490.0 - 440.0)
            b = 1.0
        elif 490.0 <= wl < 510.0:
            r = 0.0
            g = 1.0
            b = -(wl - 510.0) / (510.0 - 490.0)
        elif 510.0 <= wl < 580.0:
            r = (wl - 510.0) / (580.0 - 510.0)
            g = 1.0
            b = 0.0
        elif 580.0 <= wl < 645.0:
            r = 1.0
            g = -(wl - 645.0) / (645.0 - 580.0)
            b = 0.0
        elif 645.0 <= wl <= 780.0:
            r = 1.0
            g = 0.0
            b = 0.0
        elif wl < 380.0:
            # Ultraviolet fallback (Fluorescent violet)
            return (138, 43, 226)
        else:
            # Infrared fallback (Deep ruby red)
            return (178, 34, 34)

        # 2. Human Photopic Eye Sensitivity Falloff at vision boundaries
        if 380.0 <= wl < 420.0:
            factor = 0.3 + 0.7 * (wl - 380.0) / (420.0 - 380.0)
        elif 420.0 <= wl <= 700.0:
            factor = 1.0
        else:
            factor = 0.3 + 0.7 * (780.0 - wl) / (780.0 - 700.0)

        r_out = int(round(255.0 * ((r * factor) ** gamma))) if r > 0 else 0
        g_out = int(round(255.0 * ((g * factor) ** gamma))) if g > 0 else 0
        b_out = int(round(255.0 * ((b * factor) ** gamma))) if b > 0 else 0

        return (
            max(0, min(255, r_out)),
            max(0, min(255, g_out)),
            max(0, min(255, b_out))
        )

    @staticmethod
    def wavelength_to_hex(wavelength_nm: float) -> str:
        """Converts wavelength (nm) directly to #RRGGBB hex string."""
        r, g, b = ColorUtils.wavelength_to_rgb(wavelength_nm)
        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def generate_spectrum_strip(width: int = 800, height: int = 24) -> np.ndarray:
        """
        Synthesizes an RGB image array (height, width, 3) representing
        the continuous visible spectrum from 380 nm to 750 nm.
        """
        wls = np.linspace(380.0, 750.0, width)
        row = np.zeros((width, 3), dtype=np.uint8)
        for i, wl in enumerate(wls):
            row[i] = ColorUtils.wavelength_to_rgb(wl)

        strip = np.tile(row[np.newaxis, :, :], (height, 1, 1))
        return strip

    @staticmethod
    def blend_color(rgb: Tuple[int, int, int], bg: Tuple[int, int, int], alpha: float) -> Tuple[int, int, int]:
        """Blends RGB with background RGB according to alpha in [0.0, 1.0]."""
        a = max(0.0, min(1.0, alpha))
        r = int(round(rgb[0] * a + bg[0] * (1.0 - a)))
        g = int(round(rgb[1] * a + bg[1] * (1.0 - a)))
        b = int(round(rgb[2] * a + bg[2] * (1.0 - a)))
        return (r, g, b)
