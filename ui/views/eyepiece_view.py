"""
Interactive Eyepiece & Reticle View (دید درون چشمی تلسکوپ).
Renders high-fidelity dark optical field of view with crosshairs (reticle),
luminous spectral slit images with multi-stage bloom, focus blur, grating leveling tilt,
and realistic glass edge chromatic aberration.
Supports both Grating diffraction and Prism refraction modes.
"""

import math
import tkinter as tk
from typing import List, Optional, Tuple, Callable, Any
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel
from physics.error_model import SpectrometerErrorModel
from physics.constants import SpectralSource
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class EyepieceView(ctk.CTkFrame):
    """
    Renders the view seen by the human observer through the telescope eyepiece.
    """

    def __init__(
        self,
        master,
        model: SpectrometerModel,
        error_model: SpectrometerErrorModel,
        on_angle_change: Optional[Callable[[float], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.model = model
        self.error_model = error_model
        self.on_angle_change = on_angle_change

        self.reticle_brightness = 0.8
        self.fov_deg = 3.0  # Total angular FOV = 3.0 degrees (+/- 1.5°)
        self.darkroom_mode = False

        # Drag state for fine manual panning
        self._drag_start_x = 0
        self._drag_start_angle = 0.0

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            bg="#0A0A0E",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Mouse bindings for interactive panning through the eyepiece
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Configure>", lambda e: self.render_eyepiece())

    def _on_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_angle = self.model.effective_telescope_angle

    def _on_drag(self, event):
        dx = event.x - self._drag_start_x
        w = max(self.canvas.winfo_width(), 200)
        deg_per_px = self.fov_deg / w
        new_angle = self._drag_start_angle - (dx * deg_per_px)

        if self.model.is_clamped:
            offset = new_angle - self.model.clamp_base_angle_deg
            self.model.set_fine_tangent(offset)
        else:
            self.model.set_coarse_angle(new_angle)

        if self.on_angle_change:
            self.on_angle_change(self.model.effective_telescope_angle)

    def render_eyepiece(self, peaks: Optional[List[Any]] = None, source: Optional[SpectralSource] = None):
        """Redraws the dark optical circle, reticle crosshairs, and spectral lines."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        cx = w / 2.0
        cy = h / 2.0
        r_fov = min(w, h) * 0.44

        # Background color: deeper black in darkroom mode
        bg_room = "#030305" if self.darkroom_mode else "#0A0A0E"
        fov_fill = "#020203" if self.darkroom_mode else "#060608"

        # 1. Dark Lab Background & Outer Mask
        self.canvas.create_rectangle(0, 0, w, h, fill=bg_room, outline="")
        # Optical FOV circle
        self.canvas.create_oval(
            cx - r_fov, cy - r_fov, cx + r_fov, cy + r_fov,
            fill=fov_fill, outline="#2A2A35", width=3
        )

        # Eyepiece vignette gradient rings (simulation of tube baffle & chromatic glass edge)
        for dr in range(1, 10):
            rad = r_fov - dr
            shade = max(2, int(dr * 1.8))
            self.canvas.create_oval(
                cx - rad, cy - rad, cx + rad, cy + rad,
                outline=f"#{shade:02x}{shade:02x}{shade+2:02x}", width=1
            )
        # Subtle chromatic aberration violet/blue edge fringe on glass boundary
        self.canvas.create_oval(cx - r_fov + 2, cy - r_fov + 2, cx + r_fov - 2, cy + r_fov - 2, outline="#1E1B4B", width=1)

        tele_angle = self.model.effective_telescope_angle
        blur_factor = self.error_model.get_focus_blur_factor()
        y_drift_norm, slit_slant_deg = self.error_model.get_grating_tilt_offsets(tele_angle)
        y_center_offset = y_drift_norm * (r_fov * 0.6)

        # 2. Continuous White Light Spectrum (if continuous source)
        if source and source.is_continuous:
            for x_px in range(int(cx - r_fov), int(cx + r_fov), 3):
                dx = x_px - cx
                if abs(dx) > r_fov:
                    continue
                ang_offset = (dx / r_fov) * (self.fov_deg / 2.0)
                eval_ang = tele_angle + ang_offset
                col = "#111116"
                if abs(eval_ang) < 0.6:
                    col = "#FFFFFF" # Central white
                else:
                    d_nm = 1666.67
                    wl_nm = abs(d_nm * math.sin(math.radians(eval_ang)))
                    if 380 <= wl_nm <= 750:
                        col = ColorUtils.wavelength_to_hex(wl_nm)
                if col != "#111116":
                    y_len = math.sqrt(max(0, r_fov**2 - dx**2)) * 0.92
                    self.canvas.create_line(x_px, cy - y_len, x_px, cy + y_len, fill=col, width=3)

        # 3. Discrete Spectral Lines with Physical Glow & Thermal Broadening
        centered_peak: Optional[Any] = None
        if peaks:
            for p in peaks:
                is_missing = getattr(p, "is_missing_order", False)
                if is_missing or p.intensity <= 0:
                    continue

                # Angular distance from current telescope optical axis
                delta_ang = p.angle_deg - tele_angle
                delta_ang = (delta_ang + 180.0) % 360.0 - 180.0

                # Check if within eyepiece FOV (+/- 1.5°)
                if abs(delta_ang) <= (self.fov_deg / 2.0):
                    if abs(delta_ang) < 0.04:
                        centered_peak = p

                    # Screen X position
                    x_pos = cx + (delta_ang / (self.fov_deg / 2.0)) * r_fov

                    if abs(x_pos - cx) >= r_fov:
                        continue

                    # Vertical length restricted by circular aperture
                    dx = x_pos - cx
                    half_height = math.sqrt(max(0, r_fov**2 - dx**2)) * 0.94

                    y1 = cy - half_height + y_center_offset
                    y2 = cy + half_height + y_center_offset

                    # Slanted endpoints if table leveling tilt is active
                    slant_dx = half_height * math.tan(math.radians(slit_slant_deg))
                    x1 = x_pos - slant_dx
                    x2 = x_pos + slant_dx

                    # Colors
                    hex_col = ColorUtils.wavelength_to_hex(p.wavelength_nm) if not p.color_hint else p.color_hint
                    r_col, g_col, b_col = ColorUtils.wavelength_to_rgb(p.wavelength_nm)

                    # Darkroom sensitivity adaptation: boost visibility of faint lines
                    eff_intensity = (p.intensity ** 0.75) if self.darkroom_mode else p.intensity

                    # Dynamic line width based on slit width + focus blur + thermal width
                    base_width = max(1.5, eff_intensity * 3.0 * (self.model.main_scale_div_deg * 4))
                    eff_width = base_width * blur_factor

                    # Layer 1: Outer Soft Bloom
                    if blur_factor > 1.1 or eff_intensity > 0.35:
                        bloom_col = f"#{int(r_col*0.25):02X}{int(g_col*0.25):02X}{int(b_col*0.25):02X}"
                        self.canvas.create_line(
                            x1, y1, x2, y2,
                            fill=bloom_col, width=int(eff_width * 3.6), capstyle="round"
                        )

                    # Layer 2: Intermediate Halation Glow
                    halo_col = f"#{int(r_col*0.55):02X}{int(g_col*0.55):02X}{int(b_col*0.55):02X}"
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=halo_col, width=int(eff_width * 1.8), capstyle="round"
                    )

                    # Layer 3: Intense Slit Core
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=hex_col, width=max(1, int(eff_width * 0.8)), capstyle="round"
                    )

        # 4. Reticle Crosshairs (تار عنکبوتی رتیکول حکاکی‌شده)
        ret_val = int(round(255 * max(0.1, min(1.0, self.reticle_brightness))))
        ret_col = f"#{ret_val:02X}{ret_val:02X}{int(ret_val*0.8):02X}" # Warm amber phosphor
        ret_dim = f"#{int(ret_val*0.4):02X}{int(ret_val*0.4):02X}{int(ret_val*0.3):02X}"

        # Vertical central wire (alignment indicator)
        self.canvas.create_line(cx, cy - r_fov, cx, cy + r_fov, fill=ret_col, width=1)
        # Twin parallel fine wires in center
        self.canvas.create_line(cx - 3, cy - r_fov * 0.4, cx - 3, cy + r_fov * 0.4, fill=ret_dim, width=1)
        self.canvas.create_line(cx + 3, cy - r_fov * 0.4, cx + 3, cy + r_fov * 0.4, fill=ret_dim, width=1)

        # Horizontal central wire
        self.canvas.create_line(cx - r_fov, cy, cx + r_fov, cy, fill=ret_col, width=1)

        # Scale tick marks on horizontal crosshair (each 0.5° division)
        deg_step_px = (0.5 / (self.fov_deg / 2.0)) * r_fov
        for step in range(-3, 4):
            if step == 0:
                continue
            tx = cx + step * deg_step_px
            if abs(tx - cx) < r_fov:
                t_len = 8 if step % 2 == 0 else 5
                self.canvas.create_line(tx, cy - t_len, tx, cy + t_len, fill=ret_col, width=1)

        # Center reticle ring
        self.canvas.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, outline=ret_dim, width=1)

        # 5. Eyepiece HUD Overlays
        is_fa = LocalizationService.is_persian()
        font_num = FontManager.get_number_font(11, "bold")
        font_persian = FontManager.get_persian_font(10, "normal")

        # Top-Left HUD: Telescope Angle Telemetry
        ang_str = f"θ_tele = {tele_angle:.3f}°"
        v1_decomp = self.model.decompose_angle_to_vernier(tele_angle)
        vern_str = f"[{v1_decomp.readout_str}]"
        self.canvas.create_text(
            cx - r_fov + 10, cy - r_fov + 20,
            text=f"{ang_str}  {vern_str}",
            fill="#E2E8F0",
            anchor="w",
            font=font_num
        )

        # Top-Right HUD: Focus Status Badge
        focus_txt = "FOCUS: OPTIMAL" if blur_factor <= 1.2 else f"DEFOCUS: {blur_factor:.1f}x"
        focus_col = "#10B981" if blur_factor <= 1.2 else "#F59E0B"
        self.canvas.create_text(
            cx + r_fov - 10, cy - r_fov + 20,
            text=focus_txt,
            fill=focus_col,
            anchor="e",
            font=font_num
        )

        # Bottom HUD: Target Spectral Line Identification
        if centered_peak:
            order_info = f", m={centered_peak.order_m}" if hasattr(centered_peak, "order_m") else f", n={centered_peak.refractive_index_n:.4f}"
            line_lbl = f"ALIGNMENT: {centered_peak.line_name} (λ = {centered_peak.wavelength_nm:.2f} nm{order_info})"
            self.canvas.create_text(
                cx, cy + r_fov - 24,
                text=line_lbl,
                fill=centered_peak.color_hint or "#00F0FF",
                anchor="center",
                font=font_num
            )
        else:
            hint_txt = "موس را برای چرخش تلسکوپ بکشید — خط را در مرکز تنظیم کنید" if is_fa else "Drag horizontally to pan | Center line on crosshairs"
            LocalizationService.render_canvas_persian(
                self.canvas,
                cx, cy + r_fov - 24,
                text=hint_txt,
                fill="#94A3B8",
                anchor="center",
                font=font_persian if is_fa else font_num
            )
