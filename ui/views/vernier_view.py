"""
Dual Vernier Loupe View (بزرگ‌نمای ذره‌بین ورنیه‌های دوطرفه).
Provides high-magnification simulation of the 30-arcminute circular scale and
30-division Vernier plate with 1-arcminute precision.
Fully interactive: mouse dragging, scroll wheel micro-stepping, step buttons,
and step-by-step reading breakdown.
"""

import math
import tkinter as tk
from typing import Tuple, Optional, Callable
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel, VernierReading
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.audio_effects import AudioEffects
from utils.numeric_input import NumericInput

class VernierView(ctk.CTkFrame):
    """
    Renders high-resolution interactive magnifier views for Vernier 1 and Vernier 2.
    Allows rotating the scale directly by dragging on the loupe or using step buttons.
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
        self.show_helper = True

        self._drag_start_x = 0
        self._drag_start_angle = 0.0

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()
        font_title = FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        font_lbl = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        font_num = FontManager.get_number_font(11, "bold")
        font_btn = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")

        # ----------------------------------------------------------------------
        # ROW 0: Top Status & Mode Toggle Bar
        # ----------------------------------------------------------------------
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 2))

        self.helper_switch = ctk.CTkSwitch(
            top_bar,
            text=LocalizationService.t("sw_digital_helper"),
            font=font_title,
            command=self._on_toggle_helper
        )
        if self.show_helper:
            self.helper_switch.select()
        self.helper_switch.pack(side="left" if not is_fa else "right", padx=8)

        # Corrected Angle Badge (Always Vazirmatn for Persian text)
        self.eccentricity_lbl = ctk.CTkLabel(
            top_bar,
            text="جبران خروج از مرکز: فعال" if is_fa else "Eccentricity Compensation: Active",
            font=font_lbl,
            text_color="#38BDF8"
        )
        self.eccentricity_lbl.pack(side="right" if not is_fa else "left", padx=8)

        # ----------------------------------------------------------------------
        # ROW 1: Dual Loupes (Canvas V1 & Canvas V2)
        # ----------------------------------------------------------------------
        # Left Frame: Vernier 1
        v1_frame = ctk.CTkFrame(self, fg_color="#131318", corner_radius=8, border_width=1, border_color="#2A2A38")
        v1_frame.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)
        v1_frame.grid_columnconfigure(0, weight=1)
        v1_frame.grid_rowconfigure(1, weight=1)

        self.v1_title_lbl = ctk.CTkLabel(
            v1_frame,
            text=LocalizationService.t("vernier_1_title"),
            font=font_title,
            text_color="#F8FAFC"
        )
        self.v1_title_lbl.grid(row=0, column=0, pady=3)

        self.canvas_v1 = tk.Canvas(v1_frame, bg="#0E0E12", highlightthickness=0, cursor="sb_h_double_arrow")
        self.canvas_v1.grid(row=1, column=0, sticky="nsew", padx=6, pady=2)

        self.v1_readout_lbl = ctk.CTkLabel(
            v1_frame,
            text="Reading: --° --'",
            font=font_lbl,
            text_color="#38BDF8"
        )
        self.v1_readout_lbl.grid(row=2, column=0, pady=(2, 4))

        # Right Frame: Vernier 2
        v2_frame = ctk.CTkFrame(self, fg_color="#131318", corner_radius=8, border_width=1, border_color="#2A2A38")
        v2_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=4)
        v2_frame.grid_columnconfigure(0, weight=1)
        v2_frame.grid_rowconfigure(1, weight=1)

        self.v2_title_lbl = ctk.CTkLabel(
            v2_frame,
            text=LocalizationService.t("vernier_2_title"),
            font=font_title,
            text_color="#F8FAFC"
        )
        self.v2_title_lbl.grid(row=0, column=0, pady=3)

        self.canvas_v2 = tk.Canvas(v2_frame, bg="#0E0E12", highlightthickness=0, cursor="sb_h_double_arrow")
        self.canvas_v2.grid(row=1, column=0, sticky="nsew", padx=6, pady=2)

        self.v2_readout_lbl = ctk.CTkLabel(
            v2_frame,
            text="Reading: --° --'",
            font=font_lbl,
            text_color="#C084FC"
        )
        self.v2_readout_lbl.grid(row=2, column=0, pady=(2, 4))

        # Mouse bindings on Loupe Canvases for direct interactive dragging & scrolling
        for cv in (self.canvas_v1, self.canvas_v2):
            cv.bind("<ButtonPress-1>", self._on_loupe_press)
            cv.bind("<B1-Motion>", self._on_loupe_drag)
            cv.bind("<MouseWheel>", self._on_loupe_wheel)
            cv.bind("<Configure>", lambda e: self.render_verniers())

        # ----------------------------------------------------------------------
        # ROW 2: Direct Vernier Rotation & Micro-Stepping Toolbar
        # ----------------------------------------------------------------------
        nav_frame = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, height=42)
        nav_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(2, 4))

        # Left Micro-Stepping Buttons
        step_box_l = ctk.CTkFrame(nav_frame, fg_color="transparent")
        step_box_l.pack(side="left", padx=6, pady=4)

        ctk.CTkButton(step_box_l, text="-1°", width=38, height=26, font=font_num, command=lambda: self._step_angle(-1.0)).pack(side="left", padx=1)
        ctk.CTkButton(step_box_l, text="-10'", width=42, height=26, font=font_num, command=lambda: self._step_angle(-10.0/60.0)).pack(side="left", padx=1)
        ctk.CTkButton(step_box_l, text="◀ -1'", width=44, height=26, font=font_num, fg_color="#0284C7", hover_color="#0369A1", command=lambda: self._step_angle(-1.0/60.0)).pack(side="left", padx=1)

        # Center Angle Slider
        self.angle_slider = ctk.CTkSlider(
            nav_frame,
            from_=0.0,
            to=360.0,
            number_of_steps=720,
            command=self._on_slider_move
        )
        self.angle_slider.set(self.model.effective_telescope_angle)
        self.angle_slider.pack(side="left", fill="x", expand=True, padx=8)

        # Right Micro-Stepping Buttons
        step_box_r = ctk.CTkFrame(nav_frame, fg_color="transparent")
        step_box_r.pack(side="right", padx=6, pady=4)

        ctk.CTkButton(step_box_r, text="+1' ▶", width=44, height=26, font=font_num, fg_color="#0284C7", hover_color="#0369A1", command=lambda: self._step_angle(1.0/60.0)).pack(side="left", padx=1)
        ctk.CTkButton(step_box_r, text="+10'", width=42, height=26, font=font_num, command=lambda: self._step_angle(10.0/60.0)).pack(side="left", padx=1)
        ctk.CTkButton(step_box_r, text="+1°", width=38, height=26, font=font_num, command=lambda: self._step_angle(1.0)).pack(side="left", padx=1)

    # ==========================================================================
    # Interactive Event Handlers
    # ==========================================================================
    def _on_loupe_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_angle = self.model.effective_telescope_angle

    def _on_loupe_drag(self, event):
        dx = event.x - self._drag_start_x
        # 1 pixel = 0.04 degrees
        delta = -(dx * 0.04)
        new_ang = (self._drag_start_angle + delta) % 360.0

        if self.model.is_clamped:
            diff = (new_ang - self.model.clamp_base_angle_deg + 180.0) % 360.0 - 180.0
            self.model.set_fine_tangent(diff)
        else:
            self.model.set_coarse_angle(new_ang)

        self.angle_slider.set(self.model.effective_telescope_angle)
        AudioEffects.play_vernier_tick()

        if self.on_angle_change:
            self.on_angle_change(self.model.effective_telescope_angle)

    def _on_loupe_wheel(self, event):
        step_dir = 1 if event.delta > 0 else -1
        self._step_angle(step_dir * (1.0 / 60.0))

    def _step_angle(self, delta_deg: float):
        curr = self.model.effective_telescope_angle
        new_ang = (curr + delta_deg) % 360.0

        if self.model.is_clamped:
            diff = (new_ang - self.model.clamp_base_angle_deg + 180.0) % 360.0 - 180.0
            self.model.set_fine_tangent(diff)
        else:
            self.model.set_coarse_angle(new_ang)

        self.angle_slider.set(self.model.effective_telescope_angle)
        AudioEffects.play_vernier_tick()

        if self.on_angle_change:
            self.on_angle_change(self.model.effective_telescope_angle)

    def _on_slider_move(self, val: float):
        if not self.model.is_clamped:
            self.model.set_coarse_angle(val)
        else:
            diff = (val - self.model.clamp_base_angle_deg + 180.0) % 360.0 - 180.0
            self.model.set_fine_tangent(diff)

        if self.on_angle_change:
            self.on_angle_change(self.model.effective_telescope_angle)

    def refresh_language(self):
        """Updates text labels and fonts when active language changes."""
        is_fa = LocalizationService.is_persian()
        font_title = FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        font_lbl = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")

        self.helper_switch.configure(text=LocalizationService.t("sw_digital_helper"), font=font_title)
        self.v1_title_lbl.configure(text=LocalizationService.t("vernier_1_title"), font=font_title)
        self.v2_title_lbl.configure(text=LocalizationService.t("vernier_2_title"), font=font_title)
        self.eccentricity_lbl.configure(font=font_lbl)
        self.v1_readout_lbl.configure(font=font_lbl)
        self.v2_readout_lbl.configure(font=font_lbl)
        self.render_verniers()

    def _on_toggle_helper(self):
        self.show_helper = (self.helper_switch.get() == 1)
        self.render_verniers()

    def render_verniers(self):
        """Redraws both Vernier loupes with physical brass frames and calibrated tick marks."""
        v1_decomp, v2_decomp = self.model.get_vernier_readings()
        is_fa = LocalizationService.is_persian()
        font_lbl = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")

        # Keep slider in sync
        self.angle_slider.set(self.model.effective_telescope_angle)

        # Update Readout Labels with pure Persian font
        if self.show_helper:
            v1_msr = f"{v1_decomp.degrees}° {v1_decomp.msr_arcmin:02d}'"
            v1_vsr = f"{v1_decomp.vsr_coincident:02d}'"
            self.v1_readout_lbl.configure(
                text=f"MSR: {v1_msr}  +  VSR: {v1_vsr}  =  {v1_decomp.readout_str}",
                font=font_lbl
            )

            v2_msr = f"{v2_decomp.degrees}° {v2_decomp.msr_arcmin:02d}'"
            v2_vsr = f"{v2_decomp.vsr_coincident:02d}'"
            self.v2_readout_lbl.configure(
                text=f"MSR: {v2_msr}  +  VSR: {v2_vsr}  =  {v2_decomp.readout_str}",
                font=font_lbl
            )

            corr = self.model.get_corrected_angle_from_verniers(v1_decomp, v2_decomp)
            corr_decomp = self.model.decompose_angle_to_vernier(corr)
            if is_fa:
                self.eccentricity_lbl.configure(
                    text=f"زاویه میانگین تصحیح‌شده: {corr_decomp.readout_str} ({corr:.3f}°)",
                    font=font_lbl
                )
            else:
                self.eccentricity_lbl.configure(
                    text=f"θ_corrected = (V₁ + [V₂ - 180°]) / 2 = {corr_decomp.readout_str} ({corr:.3f}°)",
                    font=FontManager.get_number_font(11, "bold")
                )
        else:
            txt_mode = "[حالت تمرین: زاویه را از درون ذره‌بین بخوانید]" if is_fa else "[Practice Mode: Read Scale Visually]"
            self.v1_readout_lbl.configure(text=txt_mode, font=font_lbl)
            self.v2_readout_lbl.configure(text=txt_mode, font=font_lbl)
            self.eccentricity_lbl.configure(text="حالت تمرین خوانش ورنیه" if is_fa else "Helper Hidden", font=font_lbl)

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
        rim_color = "#B45309" if is_v1 else "#7E22CE"
        canvas.create_oval(cx - r_loupe - 8, cy - r_loupe - 8, cx + r_loupe + 8, cy + r_loupe + 8, fill="#1C1917", outline=rim_color, width=4)
        canvas.create_oval(cx - r_loupe, cy - r_loupe, cx + r_loupe, cy + r_loupe, fill="#0F172A", outline="#334155", width=2)

        # Specular curved glass glare
        canvas.create_arc(
            cx - r_loupe + 6, cy - r_loupe + 6, cx + r_loupe - 6, cy + r_loupe - 6,
            start=45, extent=90, style=tk.ARC, outline="#38BDF8", width=1.5
        )

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
