"""
Dual Vernier Loupe View (بزرگ‌نمای ذره‌بین ورنیه‌های دوطرفه).
Provides high-magnification simulation of the 30-arcminute circular scale and
30-division Vernier plate with 1-arcminute precision.
Supports Helper Mode (highlight coincident mark) and Practice Quiz Mode.
"""

import math
import tkinter as tk
from typing import Tuple, Optional
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel, VernierReading
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class VernierView(ctk.CTkFrame):
    """
    Renders high-resolution magnifier views for Vernier 1 and Vernier 2.
    """

    def __init__(self, master, model: SpectrometerModel, **kwargs):
        super().__init__(master, **kwargs)
        self.model = model
        self.show_helper = True

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()
        font_title = FontManager.get_ui_font(13, "bold", is_fa)
        font_num = FontManager.get_number_font(11, "bold")

        # Top Control & Toggle Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 2))

        self.helper_switch = ctk.CTkSwitch(
            top_bar,
            text=LocalizationService.t("sw_digital_helper"),
            font=font_title,
            command=self._on_toggle_helper
        )
        if self.show_helper:
            self.helper_switch.select()
        self.helper_switch.pack(side="left", padx=8)

        self.eccentricity_lbl = ctk.CTkLabel(
            top_bar,
            text=LocalizationService.t("eccentricity_active"),
            font=font_num,
            text_color="#38BDF8"
        )
        self.eccentricity_lbl.pack(side="right", padx=8)

        # Left Canvas: Vernier 1 (V1 - Primary)
        v1_frame = ctk.CTkFrame(self, fg_color="#131318", corner_radius=8, border_width=1, border_color="#2A2A35")
        v1_frame.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=6)
        v1_frame.grid_columnconfigure(0, weight=1)
        v1_frame.grid_rowconfigure(1, weight=1)

        self.v1_title_lbl = ctk.CTkLabel(
            v1_frame,
            text=LocalizationService.t("vernier_1_title"),
            font=font_title,
            text_color="#F8FAFC"
        )
        self.v1_title_lbl.grid(row=0, column=0, pady=4)

        self.canvas_v1 = tk.Canvas(v1_frame, bg="#0E0E12", highlightthickness=0)
        self.canvas_v1.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        self.v1_readout_lbl = ctk.CTkLabel(
            v1_frame,
            text="Reading: --° --'",
            font=font_num,
            text_color="#38BDF8"
        )
        self.v1_readout_lbl.grid(row=2, column=0, pady=(2, 6))

        # Right Canvas: Vernier 2 (V2 - 180° Diametric)
        v2_frame = ctk.CTkFrame(self, fg_color="#131318", corner_radius=8, border_width=1, border_color="#2A2A35")
        v2_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=6)
        v2_frame.grid_columnconfigure(0, weight=1)
        v2_frame.grid_rowconfigure(1, weight=1)

        self.v2_title_lbl = ctk.CTkLabel(
            v2_frame,
            text=LocalizationService.t("vernier_2_title"),
            font=font_title,
            text_color="#F8FAFC"
        )
        self.v2_title_lbl.grid(row=0, column=0, pady=4)

        self.canvas_v2 = tk.Canvas(v2_frame, bg="#0E0E12", highlightthickness=0)
        self.canvas_v2.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        self.v2_readout_lbl = ctk.CTkLabel(
            v2_frame,
            text="Reading: --° --'",
            font=font_num,
            text_color="#A855F7"
        )
        self.v2_readout_lbl.grid(row=2, column=0, pady=(2, 6))

        # Resize bindings
        self.canvas_v1.bind("<Configure>", lambda e: self.render_verniers())
        self.canvas_v2.bind("<Configure>", lambda e: self.render_verniers())

    def refresh_language(self):
        """Updates text labels when active language changes."""
        is_fa = LocalizationService.is_persian()
        font_title = FontManager.get_ui_font(13, "bold", is_fa)

        self.helper_switch.configure(text=LocalizationService.t("sw_digital_helper"), font=font_title)
        self.eccentricity_lbl.configure(text=LocalizationService.t("eccentricity_active"))
        self.v1_title_lbl.configure(text=LocalizationService.t("vernier_1_title"), font=font_title)
        self.v2_title_lbl.configure(text=LocalizationService.t("vernier_2_title"), font=font_title)
        self.render_verniers()

    def _on_toggle_helper(self):
        self.show_helper = self.helper_switch.get() == 1
        self.render_verniers()

    def render_verniers(self):
        """Redraws both Vernier loupes with physical brass frames and calibrated tick marks."""
        v1_decomp, v2_decomp = self.model.get_vernier_readings()
        is_fa = LocalizationService.is_persian()

        # Update Readout Labels
        if self.show_helper:
            v1_msr = f"{v1_decomp.degrees}° {v1_decomp.msr_arcmin:02d}'"
            v1_vsr = f"{v1_decomp.vsr_coincident:02d}'"
            self.v1_readout_lbl.configure(
                text=f"MSR: {v1_msr}  +  VSR: {v1_vsr}  =  {v1_decomp.readout_str}"
            )

            v2_msr = f"{v2_decomp.degrees}° {v2_decomp.msr_arcmin:02d}'"
            v2_vsr = f"{v2_decomp.vsr_coincident:02d}'"
            self.v2_readout_lbl.configure(
                text=f"MSR: {v2_msr}  +  VSR: {v2_vsr}  =  {v2_decomp.readout_str}"
            )

            corr = self.model.get_corrected_angle_from_verniers(v1_decomp, v2_decomp)
            corr_decomp = self.model.decompose_angle_to_vernier(corr)
            if is_fa:
                self.eccentricity_lbl.configure(
                    text=f"زاویه تصحیح‌شده: {corr_decomp.readout_str} ({corr:.3f}°)"
                )
            else:
                self.eccentricity_lbl.configure(
                    text=f"θ_corrected = (V₁ + [V₂ - 180°]) / 2 = {corr_decomp.readout_str} ({corr:.3f}°)"
                )
        else:
            txt_mode = "[حالت تمرین: زاویه را با ذره‌بین بخوانید]" if is_fa else "[Practice Mode: Read Scale Visually]"
            self.v1_readout_lbl.configure(text=txt_mode)
            self.v2_readout_lbl.configure(text=txt_mode)
            self.eccentricity_lbl.configure(text="حالت تمرین" if is_fa else "Helper Hidden")

        # Render on canvases
        self._draw_loupe(self.canvas_v1, v1_decomp, is_v1=True)
        self._draw_loupe(self.canvas_v2, v2_decomp, is_v1=False)

    def _draw_loupe(self, canvas: tk.Canvas, decomp: VernierReading, is_v1: bool):
        """Draws a circular magnifying glass with main scale and vernier arcs."""
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 50 or h < 50:
            return

        cx = w / 2.0
        cy = h / 2.0
        r_loupe = min(w, h) * 0.44

        # 1. Brass Loupe Rim & Convex Glass Highlight
        rim_color = "#B45309" if is_v1 else "#7E22CE" # Amber / Purple brass
        canvas.create_oval(cx - r_loupe - 8, cy - r_loupe - 8, cx + r_loupe + 8, cy + r_loupe + 8, fill="#1C1917", outline=rim_color, width=4)
        canvas.create_oval(cx - r_loupe, cy - r_loupe, cx + r_loupe, cy + r_loupe, fill="#0F172A", outline="#334155", width=2)

        # Scale parameters
        r_split = r_loupe * 0.58
        font_scale = FontManager.get_number_font(9, "bold")

        angle_deg = decomp.raw_angle_deg
        arc_zoom = 14.0

        # 2. Main Circular Scale (Outer arc, divisions every 30' = 0.5°)
        min_mark = int(math.floor((angle_deg - 6.0) * 2.0))
        max_mark = int(math.ceil((angle_deg + 6.0) * 2.0))

        for mark_idx in range(min_mark, max_mark + 1):
            mark_deg = mark_idx * 0.5
            delta_deg = mark_deg - angle_deg
            loupe_deg = 270.0 + (delta_deg * arc_zoom)
            rad = math.radians(loupe_deg)

            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            is_degree = (mark_idx % 2 == 0)
            is_five_deg = (mark_idx % 10 == 0)

            tick_len = 22 if is_five_deg else (16 if is_degree else 11)
            r1 = r_split
            r2 = r_split + tick_len

            x1 = cx + r1 * cos_a
            y1 = cy + r1 * sin_a
            x2 = cx + r2 * cos_a
            y2 = cy + r2 * sin_a

            canvas.create_line(x1, y1, x2, y2, fill="#E2E8F0" if is_degree else "#94A3B8", width=2 if is_degree else 1)

            # Degree labels on major marks
            if is_five_deg or (is_degree and abs(delta_deg) < 3.0):
                lbl_val = int(round(mark_deg)) % 360
                r_lbl = r2 + 10
                lx = cx + r_lbl * cos_a
                ly = cy + r_lbl * sin_a
                canvas.create_text(lx, ly, text=str(lbl_val), fill="#F8FAFC", font=font_scale)

        # 3. Sliding Vernier Plate (Inner arc, 30 divisions = 29 main scale divisions)
        for v_idx in range(31):
            v_offset_deg = v_idx * (29.0 / 30.0) * 0.5
            loupe_deg = 270.0 + (v_offset_deg * arc_zoom)
            rad = math.radians(loupe_deg)

            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            is_coincident = (v_idx == decomp.vsr_coincident)
            is_major_v = (v_idx % 5 == 0)

            tick_len = 20 if is_major_v else 12
            r1 = r_split - tick_len
            r2 = r_split

            x1 = cx + r1 * cos_a
            y1 = cy + r1 * sin_a
            x2 = cx + r2 * cos_a
            y2 = cy + r2 * sin_a

            if self.show_helper and is_coincident:
                canvas.create_line(x1, y1, x2, y2, fill="#00F0FF", width=3)
                tx = cx + (r_split + 6) * cos_a
                ty = cy + (r_split + 6) * sin_a
                canvas.create_oval(tx - 3, ty - 3, tx + 3, ty + 3, fill="#00F0FF", outline="")
            else:
                canvas.create_line(x1, y1, x2, y2, fill="#CBD5E1" if is_major_v else "#64748B", width=2 if is_major_v else 1)

            if v_idx in (0, 10, 20, 30):
                r_lbl = r1 - 10
                lx = cx + r_lbl * cos_a
                ly = cy + r_lbl * sin_a
                canvas.create_text(lx, ly, text=str(v_idx), fill="#38BDF8" if is_v1 else "#C084FC", font=font_scale)

        # 4. Dividing Boundary Line
        canvas.create_oval(cx - r_split, cy - r_split, cx + r_split, cy + r_split, outline="#475569", width=1)

        # 5. Central Index Mark (Vernier Zero Indicator)
        canvas.create_line(cx, cy - r_split - 4, cx, cy - r_split + 8, fill="#EF4444", width=2)
