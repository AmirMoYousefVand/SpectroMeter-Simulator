"""
1D Spectral Intensity Curve & Photographic Spectrum Strip View (پروفایل شدت طیف).
Plots analytical Fraunhofer intensity I(θ) vs. deflection angle with fast updates,
photographic visible spectrum strip, and peak wavelength annotations.
"""

from typing import List, Optional, Tuple
import customtkinter as ctk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from physics.spectrometer_model import SpectrometerModel
from physics.grating_engine import DiffractedPeak, GratingEngine
from physics.constants import SpectralSource
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class Profile1DView(ctk.CTkFrame):
    """
    Renders 1D intensity profile plot, color spectrum ribbon, and peak telemetry.
    """

    def __init__(self, master, model: SpectrometerModel, **kwargs):
        super().__init__(master, **kwargs)
        self.model = model

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Matplotlib 2D Figure
        self.fig = Figure(figsize=(7, 4.4), dpi=100, facecolor="#101014")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#121216")

        self.ax.grid(True, linestyle=":", alpha=0.3, color="#52525B")
        self.ax.tick_params(colors="#94A3B8", labelsize=8)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=8, pady=6)

    def refresh_language(self):
        """Redraws plot when language is changed."""
        pass

    def update_profile(
        self,
        grating_engine: GratingEngine,
        source: SpectralSource,
        blur_factor: float = 1.0
    ):
        """Recomputes and redraws the 1D intensity profile and peak tags."""
        tele_angle = self.model.effective_telescope_angle
        signed_dev = self.model.deviation_angle

        # Angular grid for evaluation [-65°, +65°]
        theta_grid = np.linspace(-65.0, 65.0, 1600)
        intensity, peaks = grating_engine.compute_spectrum_profile_1d(
            source, theta_grid, focus_blur_factor=blur_factor
        )

        is_fa = LocalizationService.is_persian()
        prop = FontManager.get_mpl_persian_prop(9) if is_fa else FontManager.get_mpl_number_prop(9)

        # Clear annotations and rebuild plot
        self.ax.cla()
        self.ax.set_facecolor("#121216")
        self.ax.grid(True, linestyle=":", alpha=0.3, color="#52525B")
        self.ax.tick_params(colors="#94A3B8", labelsize=8)

        # Clean axis labels without punctuation reversal
        lbl_x = LocalizationService.reshape_text("زاویه انحراف پراش (درجه)") if is_fa else "Diffraction Deviation Angle θ (deg)"
        lbl_y = LocalizationService.reshape_text("شدت نسبی نور") if is_fa else "Normalized Relative Intensity I(θ) / I₀"
        self.ax.set_xlabel(lbl_x, color="#E2E8F0", fontsize=9, fontproperties=prop)
        self.ax.set_ylabel(lbl_y, color="#E2E8F0", fontsize=9, fontproperties=prop)

        # Plot 1D Profile curve
        curve_lbl = LocalizationService.reshape_text("شدت طیف I(θ)") if is_fa else "Spectral Intensity I(θ)"
        self.ax.plot(theta_grid, intensity, color="#38BDF8", lw=1.8, label=curve_lbl)

        # Current telescope marker and FOV
        axis_lbl = LocalizationService.reshape_text("راستای تلسکوپ") if is_fa else "Telescope Axis"
        self.ax.axvline(signed_dev, color="#EF4444", lw=1.5, linestyle="--", label=axis_lbl)
        self.ax.axvspan(signed_dev - 1.5, signed_dev + 1.5, color="#38BDF8", alpha=0.12)

        # Peak Annotations (Labels with wavelength and order)
        for p in peaks:
            if p.is_missing_order or p.intensity < 0.15:
                continue
            if abs(p.angle_deg) > 65.0:
                continue

            r_hex = ColorUtils.wavelength_to_hex(p.wavelength_nm) if not p.color_hint else p.color_hint
            # Peak dot
            self.ax.scatter([p.angle_deg], [p.intensity], color=r_hex, s=36, zorder=5)

            # Text label
            lbl_text = f"{p.wavelength_nm:.1f}nm\n(m={p.order_m})"
            self.ax.annotate(
                lbl_text,
                xy=(p.angle_deg, p.intensity),
                xytext=(p.angle_deg, min(1.15, p.intensity + 0.08)),
                fontsize=7,
                color="#F1F5F9",
                ha="center",
                arrowprops=dict(arrowstyle="-", color=r_hex, lw=0.8, alpha=0.7)
            )

        self.ax.set_xlim(-65.0, 65.0)
        self.ax.set_ylim(-0.05, 1.25)
        self.ax.legend(loc="upper right", facecolor="#18181B", edgecolor="#27272A", labelcolor="#E2E8F0", prop=prop)

        self.canvas.draw()
