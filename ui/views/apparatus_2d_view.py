"""
High-Fidelity 2D Orthographic Laboratory View (نمای ارتوگرافیک بالای دستگاه).
Renders realistic top-down CAD-like apparatus: optical breadboard table, cast-iron base,
brass collimator with finned lamp housing and power cable, rotating telescope arm,
diffraction grating or equilateral glass prism, and live ray paths.
Supports interactive mouse drag rotation.
"""

import math
import tkinter as tk
from typing import List, Optional, Callable, Any
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel
from physics.constants import SpectralSource
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.audio_effects import AudioEffects

class Apparatus2DView(ctk.CTkFrame):
    """
    Renders top-down schematic apparatus diagram with rotating mechanical components and ray tracing.
    """

    def __init__(
        self,
        master,
        model: SpectrometerModel,
        on_angle_change: Optional[Callable[[float], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.model = model
        self.on_angle_change = on_angle_change

        self.optic_mode = "grating" # "grating" or "prism"
        self._is_dragging = False
        self._last_tick_angle = self.model.effective_telescope_angle

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="#0E0E12", highlightthickness=0, cursor="hand2")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Mouse drag rotation bindings
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Configure>", lambda e: self.render_apparatus())

    def _on_press(self, event):
        self._is_dragging = True
        self._update_angle_from_mouse(event.x, event.y)

    def _on_drag(self, event):
        if self._is_dragging:
            self._update_angle_from_mouse(event.x, event.y)

    def _on_release(self, event):
        self._is_dragging = False

    def _update_angle_from_mouse(self, mx: float, my: float):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx = w / 2.0
        cy = h / 2.0

        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)
        if dist < 20:
            return

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) % 360.0

        if self.model.is_clamped:
            diff = (angle_deg - self.model.clamp_base_angle_deg + 180.0) % 360.0 - 180.0
            self.model.set_fine_tangent(diff)
        else:
            self.model.set_coarse_angle(angle_deg)

        curr_ang = self.model.effective_telescope_angle
        if abs(curr_ang - self._last_tick_angle) >= 0.5:
            AudioEffects.play_vernier_tick()
            self._last_tick_angle = curr_ang

        if self.on_angle_change:
            self.on_angle_change(curr_ang)

    def render_apparatus(
        self,
        peaks: Optional[List[Any]] = None,
        source: Optional[SpectralSource] = None
    ):
        """Redraws the physical spectrometer apparatus and optical rays."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 60 or h < 60:
            return

        cx = w / 2.0
        cy = h / 2.0
        r_scale = min(w, h) * 0.32

        # 0. Optical Breadboard Grid (Threaded M6 Mounting Holes)
        grid_step = 28
        for gx in range(0, w, grid_step):
            for gy in range(0, h, grid_step):
                self.canvas.create_oval(gx - 1, gy - 1, gx + 1, gy + 1, fill="#1F2937", outline="")

        # 1. Base Stand: Cast Iron Outer Chassis & Leveling Feet
        self.canvas.create_oval(cx - r_scale - 32, cy - r_scale - 32, cx + r_scale + 32, cy + r_scale + 32, fill="#18181F", outline="#2A2A38", width=3)
        for foot_ang in (30, 150, 270):
            fx = cx + (r_scale + 38) * math.cos(math.radians(foot_ang))
            fy = cy + (r_scale + 38) * math.sin(math.radians(foot_ang))
            self.canvas.create_oval(fx - 14, fy - 14, fx + 14, fy + 14, fill="#3F3F46", outline="#D97706", width=2)
            self.canvas.create_text(fx, fy, text="✛", fill="#F59E0B", font=("Arial", 11, "bold"))

        # 2. Graduated Circular Scale (0° to 360°)
        self.canvas.create_oval(cx - r_scale, cy - r_scale, cx + r_scale, cy + r_scale, fill="#1E1E24", outline="#475569", width=2)
        for deg in range(0, 360, 5):
            rad = math.radians(deg)
            is_major = (deg % 10 == 0)
            t_len = 10 if is_major else 6
            x1 = cx + (r_scale - t_len) * math.cos(rad)
            y1 = cy + (r_scale - t_len) * math.sin(rad)
            x2 = cx + r_scale * math.cos(rad)
            y2 = cy + r_scale * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="#E2E8F0" if is_major else "#64748B", width=1)
            if deg % 30 == 0:
                tx = cx + (r_scale - 18) * math.cos(rad)
                ty = cy + (r_scale - 18) * math.sin(rad)
                self.canvas.create_text(tx, ty, text=str(deg), fill="#94A3B8", font=("Space Grotesk", 7, "bold"))

        # 3. Fixed Collimator Arm (Brass Tube)
        coll_len = r_scale * 1.35
        coll_w = 16
        self.canvas.create_rectangle(cx - coll_len, cy - coll_w/2, cx - 35, cy + coll_w/2, fill="#B45309", outline="#D97706", width=1)

        # Realistic Finned Lamp Housing Box
        box_x0 = cx - coll_len - 38
        box_x1 = cx - coll_len
        box_y0 = cy - 28
        box_y1 = cy + 28
        self.canvas.create_rectangle(box_x0, box_y0, box_x1, box_y1, fill="#27272A", outline="#71717A", width=2)
        # Cooling Fins
        for fy in range(int(box_y0 + 6), int(box_y1 - 4), 6):
            self.canvas.create_line(box_x0 - 5, fy, box_x0, fy, fill="#52525B", width=2)

        # Power Rocker Switch & Lamp Filament Glow
        self.canvas.create_rectangle(box_x0 + 4, box_y0 + 4, box_x0 + 12, box_y0 + 12, fill="#DC2626", outline="#991B1B") # Red switch
        lamp_hex = "#F59E0B"
        if source and source.lines:
            lamp_hex = ColorUtils.wavelength_to_hex(source.lines[0].wavelength_nm)
        self.canvas.create_oval(cx - coll_len - 22, cy - 10, cx - coll_len - 8, cy + 10, fill=lamp_hex, outline="")
        # Power Cable running to left
        self.canvas.create_line(box_x0, box_y1 - 8, box_x0 - 24, box_y1 + 18, box_x0 - 60, box_y1 + 22, fill="#0F172A", width=3)

        disp_title = source.name_fa if LocalizationService.is_persian() and source else (source.name_en if source else "Lamp")
        self.canvas.create_text(cx - coll_len - 18, cy - 36, text=disp_title, fill="#F8FAFC", font=FontManager.get_ui_font(8, "bold", LocalizationService.is_persian()))

        # Collimated parallel light beam (from slit to central optic)
        self.canvas.create_polygon(
            cx - coll_len, cy - 6,
            cx, cy - 6,
            cx, cy + 6,
            cx - coll_len, cy + 6,
            fill="#FEF08A", stipple="gray50", outline=""
        )

        # 4. Optical Rays Radiating to Telescope
        if peaks:
            for p in peaks:
                is_missing = getattr(p, "is_missing_order", False)
                if is_missing or p.intensity <= 0:
                    continue
                p_rad = math.radians(p.angle_deg)
                ray_len = r_scale * 1.2
                rx = cx + ray_len * math.cos(p_rad)
                ry = cy + ray_len * math.sin(p_rad)
                r_hex = ColorUtils.wavelength_to_hex(p.wavelength_nm) if not p.color_hint else p.color_hint

                is_order0 = getattr(p, "order_m", None) == 0
                dash_style = () if is_order0 else (4, 3)
                ray_w = 3 if is_order0 else max(1, int(p.intensity * 2.5))
                self.canvas.create_line(cx, cy, rx, ry, fill=r_hex, width=ray_w, dash=dash_style)

        # 5. Central Rotating Stage
        r_stage = 36
        self.canvas.create_oval(cx - r_stage, cy - r_stage, cx + r_stage, cy + r_stage, fill="#27272A", outline="#71717A", width=2)
        for sc_ang in (0, 120, 240):
            sx = cx + 24 * math.cos(math.radians(sc_ang))
            sy = cy + 24 * math.sin(math.radians(sc_ang))
            self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#F59E0B", outline="")

        # 5.B Optic: Grating Plate vs Triangular Prism
        if self.optic_mode == "prism":
            # Equilateral Glass Prism (A = 60° at center)
            pr_side = 32
            # Triangle pointing right
            p_top = (cx - 10, cy - pr_side * 0.866)
            p_bot = (cx - 10, cy + pr_side * 0.866)
            p_apex = (cx + pr_side * 0.866 - 10, cy)
            self.canvas.create_polygon(
                p_top[0], p_top[1],
                p_bot[0], p_bot[1],
                p_apex[0], p_apex[1],
                fill="#38BDF8", outline="#BAE6FD", width=2, stipple="gray50"
            )
            self.canvas.create_text(cx - 2, cy, text="PRISM", fill="#0369A1", font=("Space Grotesk", 7, "bold"))
        else:
            # Transmission Diffraction Grating Plate (Rectangular glass block)
            g_h = 32
            g_w = 6
            self.canvas.create_rectangle(cx - g_w/2, cy - g_h/2, cx + g_w/2, cy + g_h/2, fill="#06B6D4", outline="#A5F3FC", width=1)
            for gy in range(int(cy - g_h/2 + 4), int(cy + g_h/2), 4):
                self.canvas.create_line(cx - g_w/2 + 1, gy, cx + g_w/2 - 1, gy, fill="#164E63")

        # 6. Rotating Telescope Arm
        tele_ang_deg = self.model.effective_telescope_angle
        tele_rad = math.radians(tele_ang_deg)
        cos_t = math.cos(tele_rad)
        sin_t = math.sin(tele_rad)

        tele_len = r_scale * 1.35
        tele_w = 16
        nx = -sin_t
        ny = cos_t

        p1_x = cx + 35 * cos_t + (tele_w/2) * nx
        p1_y = cy + 35 * sin_t + (tele_w/2) * ny
        p2_x = cx + tele_len * cos_t + (tele_w/2) * nx
        p2_y = cy + tele_len * sin_t + (tele_w/2) * ny
        p3_x = cx + tele_len * cos_t - (tele_w/2) * nx
        p3_y = cy + tele_len * sin_t - (tele_w/2) * ny
        p4_x = cx + 35 * cos_t - (tele_w/2) * nx
        p4_y = cy + 35 * sin_t - (tele_w/2) * ny

        self.canvas.create_polygon(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y, fill="#3F3F46", outline="#71717A", width=1)

        eye_x = cx + tele_len * cos_t
        eye_y = cy + tele_len * sin_t
        self.canvas.create_oval(eye_x - 12, eye_y - 12, eye_x + 12, eye_y + 12, fill="#18181B", outline="#38BDF8", width=2)
        self.canvas.create_text(eye_x + 18 * nx, eye_y + 18 * ny, text="Eyepiece", fill="#38BDF8", font=("Space Grotesk", 8, "bold"))

        clamp_x = cx + (r_scale * 0.85) * cos_t
        clamp_y = cy + (r_scale * 0.85) * sin_t
        clamp_col = "#EF4444" if self.model.is_clamped else "#10B981"
        self.canvas.create_oval(clamp_x - 7, clamp_y - 7, clamp_x + 7, clamp_y + 7, fill=clamp_col, outline="#FFFFFF", width=1)

        # 7. Dual Verniers (V1 & V2)
        v1_x = cx + r_scale * cos_t
        v1_y = cy + r_scale * sin_t
        v2_x = cx - r_scale * cos_t
        v2_y = cy - r_scale * sin_t

        self.canvas.create_oval(v1_x - 9, v1_y - 9, v1_x + 9, v1_y + 9, fill="#0284C7", outline="#38BDF8", width=2)
        self.canvas.create_text(v1_x, v1_y, text="V₁", fill="#FFFFFF", font=("Space Grotesk", 8, "bold"))

        self.canvas.create_oval(v2_x - 9, v2_y - 9, v2_x + 9, v2_y + 9, fill="#7E22CE", outline="#C084FC", width=2)
        self.canvas.create_text(v2_x, v2_y, text="V₂", fill="#FFFFFF", font=("Space Grotesk", 8, "bold"))

        # 8. HUD & Interactive Tip
        is_fa = LocalizationService.is_persian()
        font_txt = FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10)
        tip_msg = "جهت چرخاندن تلسکوپ روی آن کلیک کرده و بکشید — دایره رنگی نشان‌دهنده قفل است" if is_fa else "Click and drag telescope arm to rotate | Green/Red dot indicates clamp"
        LocalizationService.render_canvas_persian(self.canvas, cx, h - 18, text=tip_msg, fill="#94A3B8", font=font_txt)
