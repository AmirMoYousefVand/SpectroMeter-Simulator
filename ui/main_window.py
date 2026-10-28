"""
Main Application Root Window & Simulation Coordinator.
Orchestrates CustomTkinter interface, physics engines, multi-view tabs,
real-time rendering loop, hot language swapping, and multi-format report exports.
Supports Grating diffraction and Prism dispersion, darkroom ambient lighting mode,
and complete parameter resets.
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Any, Optional
import customtkinter as ctk
from PIL import Image

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APPEARANCE_MODE,
    COLOR_THEME,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_GEOMETRY,
    DEFAULT_LAMP,
    DEFAULT_GRATING
)
from physics.spectrometer_model import SpectrometerModel
from physics.grating_engine import GratingEngine, DiffractedPeak
from physics.prism_engine import PrismEngine, RefractedPeak
from physics.error_model import SpectrometerErrorModel, ErrorParameters
from utils.resource_utils import resource_path, apply_window_icon
from physics.constants import SPECTRAL_SOURCES, GRATING_PRESETS
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.audio_effects import AudioEffects
from utils.docx_exporter import DocxEquationExporter
from utils.export_service import ExportService

from ui.components.control_panel import ControlPanel
from ui.components.metrics_panel import MetricsPanel

from ui.views.eyepiece_view import EyepieceView
from ui.views.vernier_view import VernierView
from ui.views.apparatus_2d_view import Apparatus2DView
from ui.views.apparatus_3d_view import Apparatus3DView
from ui.views.profile_1d_view import Profile1DView
from ui.views.calculations_view import CalculationsView
from ui.views.guide_view import GuideView

class MainWindow(ctk.CTk):
    """
    Main application root window hosting the complete spectrometer simulator.
    """

    def __init__(self):
        super().__init__()

        # Appearance & Theme setup
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(f"{APP_TITLE} — {APP_SUBTITLE}")
        self.geometry(WINDOW_DEFAULT_GEOMETRY)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._set_window_icon()

        # Instantiate Physical Engines & Models
        self.model = SpectrometerModel()
        self.error_model = SpectrometerErrorModel()
        self.grating_engine = GratingEngine(lines_per_mm=600.0, slit_width_mm=0.05)
        self.prism_engine = PrismEngine(apex_angle_deg=60.0)

        self.optic_mode = "grating" # "grating" or "prism"

        # Cache of current diffracted/refracted peaks
        self.current_peaks = []
        self.centered_peak = None

        # Build UI Architecture
        self._create_layout()
        self._bind_shortcuts()

        # Initial full calculation & pre-render ALL views
        self._initial_render_all()

    def _set_window_icon(self):
        """Applies application icon to taskbar and title bar."""
        apply_window_icon(self)

    def _create_layout(self):
        """Constructs top bar, sidebar control panel, tabview, metrics bar, and footer."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()
        font_h = FontManager.get_ui_font(14, "bold", is_fa)
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)
        font_num = FontManager.get_number_font(10)

        # ----------------------------------------------------------------------
        # ROW 0: Top Application Bar
        # ----------------------------------------------------------------------
        top_bar = ctk.CTkFrame(self, fg_color="#181820", height=42, corner_radius=0)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Left / Right Title
        self.title_lbl = ctk.CTkLabel(
            top_bar,
            text=LocalizationService.t("app_title"),
            font=font_h,
            text_color="#38BDF8"
        )
        self.title_lbl.pack(side="left" if not is_fa else "right", padx=16, pady=6)

        # Action Switches Cluster
        btn_pack_side = "right" if not is_fa else "left"

        # Language Toggle Button (Always Vazirmatn so "فارسی (FA)" remains connected)
        self.lang_btn = ctk.CTkButton(
            top_bar,
            text=LocalizationService.t("lang_switch"),
            font=FontManager.get_persian_font(11, "bold"),
            width=90,
            height=28,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._toggle_language
        )
        self.lang_btn.pack(side=btn_pack_side, padx=5, pady=6)

        # Theme Toggle Button
        self.theme_btn = ctk.CTkButton(
            top_bar,
            text=LocalizationService.t("theme_toggle"),
            font=font_btn,
            width=68,
            height=28,
            fg_color="#3F3F46",
            hover_color="#52525B",
            command=self._toggle_theme
        )
        self.theme_btn.pack(side=btn_pack_side, padx=5, pady=6)

        # Darkroom Ambient Lighting Toggle with vector icon
        moon_img = None
        moon_path = resource_path(os.path.join("assets", "icons", "ui", "moon.png"))
        if os.path.exists(moon_path):
            try:
                pil_m = Image.open(moon_path).resize((14, 14), Image.Resampling.LANCZOS)
                moon_img = ctk.CTkImage(light_image=pil_m, dark_image=pil_m, size=(14, 14))
            except Exception:
                pass

        self.darkroom_btn = ctk.CTkButton(
            top_bar,
            image=moon_img,
            compound="left",
            text=" " + LocalizationService.t("darkroom_toggle"),
            font=font_btn,
            width=92,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            command=self._toggle_darkroom
        )
        self.darkroom_btn.pack(side=btn_pack_side, padx=5, pady=6)

        # Sound Mute Toggle with vector icon
        snd_on_path = resource_path(os.path.join("assets", "icons", "ui", "sound_on.png"))
        snd_mute_path = resource_path(os.path.join("assets", "icons", "ui", "sound_mute.png"))
        self.snd_on_img = None
        self.snd_mute_img = None
        if os.path.exists(snd_on_path):
            try:
                pil_so = Image.open(snd_on_path).resize((14, 14), Image.Resampling.LANCZOS)
                self.snd_on_img = ctk.CTkImage(light_image=pil_so, dark_image=pil_so, size=(14, 14))
                pil_sm = Image.open(snd_mute_path).resize((14, 14), Image.Resampling.LANCZOS)
                self.snd_mute_img = ctk.CTkImage(light_image=pil_sm, dark_image=pil_sm, size=(14, 14))
            except Exception:
                pass

        self.sound_btn = ctk.CTkButton(
            top_bar,
            image=self.snd_on_img,
            compound="left",
            text=" Sound",
            font=font_num,
            width=76,
            height=28,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._toggle_sound
        )
        self.sound_btn.pack(side=btn_pack_side, padx=5, pady=6)

        # ----------------------------------------------------------------------
        # ROW 1, COL 0: Left Sidebar Control Panel
        # ----------------------------------------------------------------------
        self.control_panel = ControlPanel(
            self,
            model=self.model,
            error_model=self.error_model,
            on_change=self._on_parameter_changed,
            on_record_measurement=self._record_current_measurement,
            on_reset_all=self._on_reset_all,
            on_optic_mode_change=self._on_optic_mode_changed,
            width=340
        )
        self.control_panel.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        # ----------------------------------------------------------------------
        # ROW 1, COL 1: Center Multi-View Tabs & Bottom Telemetry
        # ----------------------------------------------------------------------
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 6), pady=6)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)

        # 7-Tab Navigation View with stable internal IDs and callback
        self.tabview = ctk.CTkTabview(center_frame, command=self._on_tab_changed)
        self.tabview.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

        # Add 7 dedicated tabs with invariant string IDs
        self.tab_eye = self.tabview.add("tab_eye")
        self.tab_vern = self.tabview.add("tab_vern")
        self.tab_2d = self.tabview.add("tab_2d")
        self.tab_3d = self.tabview.add("tab_3d")
        self.tab_prof = self.tabview.add("tab_prof")
        self.tab_calc = self.tabview.add("tab_calc")
        self.tab_guide = self.tabview.add("tab_guide")

        # Configure tab frames
        for t in (self.tab_eye, self.tab_vern, self.tab_2d, self.tab_3d, self.tab_prof, self.tab_calc, self.tab_guide):
            t.grid_columnconfigure(0, weight=1)
            t.grid_rowconfigure(0, weight=1)

        # Populate View Components inside tabs
        self.view_eyepiece = EyepieceView(
            self.tab_eye,
            model=self.model,
            error_model=self.error_model,
            on_angle_change=self._on_angle_dragged
        )
        self.view_eyepiece.grid(row=0, column=0, sticky="nsew")

        self.view_vernier = VernierView(
            self.tab_vern,
            model=self.model,
            on_angle_change=self._on_angle_dragged
        )
        self.view_vernier.grid(row=0, column=0, sticky="nsew")

        self.view_apparatus_2d = Apparatus2DView(
            self.tab_2d,
            model=self.model,
            on_angle_change=self._on_angle_dragged
        )
        self.view_apparatus_2d.grid(row=0, column=0, sticky="nsew")

        self.view_apparatus_3d = Apparatus3DView(
            self.tab_3d,
            model=self.model
        )
        self.view_apparatus_3d.grid(row=0, column=0, sticky="nsew")

        self.view_profile_1d = Profile1DView(
            self.tab_prof,
            model=self.model
        )
        self.view_profile_1d.grid(row=0, column=0, sticky="nsew")

        self.view_calculations = CalculationsView(
            self.tab_calc,
            model=self.model,
            on_export_docx=self._export_docx_report,
            on_export_csv=self._export_csv_data
        )
        self.view_calculations.grid(row=0, column=0, sticky="nsew")

        self.view_guide = GuideView(self.tab_guide)
        self.view_guide.grid(row=0, column=0, sticky="nsew")

        # Set localized titles on tab segmented buttons
        self._update_tabview_titles()

        # Bottom Telemetry Status Bar
        self.metrics_panel = MetricsPanel(
            center_frame,
            model=self.model,
            on_record_click=self._record_current_measurement
        )
        self.metrics_panel.grid(row=1, column=0, sticky="ew")

        # ----------------------------------------------------------------------
        # ROW 2: Footer Bar (Copyright & GitHub Link)
        # ----------------------------------------------------------------------
        footer_bar = ctk.CTkFrame(self, fg_color="#121216", height=28, corner_radius=0)
        footer_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        copy_txt = "Optical Spectrometer Simulator © 2026 — Created for Advanced Wave Optics Education"
        ctk.CTkLabel(footer_bar, text=copy_txt, font=font_num, text_color="#64748B").pack(side="left", padx=16, pady=2)

        # GitHub Repo Link Button
        gh_img = None
        gh_path = resource_path(os.path.join("assets", "Logo", "github-mark.png"))
        if os.path.exists(gh_path):
            try:
                pil_gh = Image.open(gh_path).resize((14, 14), Image.Resampling.LANCZOS)
                gh_img = ctk.CTkImage(light_image=pil_gh, dark_image=pil_gh, size=(14, 14))
            except Exception:
                pass

        btn_gh = ctk.CTkButton(
            footer_bar,
            image=gh_img,
            text="GitHub Repository",
            font=font_num,
            fg_color="transparent",
            hover_color="#1e1e24",
            text_color="#94A3B8",
            height=22,
            width=130,
            cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://github.com/AmirMoYousefVand/SpectroMeter-Simulator")
        )
        btn_gh.pack(side="right", padx=16, pady=2)

    def _update_tabview_titles(self):
        """Updates tabview segmented button labels for the active language."""
        is_fa = LocalizationService.is_persian()
        tab_font = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        self.tabview._segmented_button.configure(font=tab_font)

        tab_map = [
            ("tab_eye", "tab_eyepiece"),
            ("tab_vern", "tab_verniers"),
            ("tab_2d", "tab_app_2d"),
            ("tab_3d", "tab_app_3d"),
            ("tab_prof", "tab_profile_1d"),
            ("tab_calc", "tab_calc"),
            ("tab_guide", "tab_guide")
        ]
        for tab_id, loc_key in tab_map:
            title = LocalizationService.t(loc_key)
            btn = self.tabview._segmented_button._buttons_dict.get(tab_id)
            if btn is not None:
                btn.configure(text=title, font=tab_font)

    def _bind_shortcuts(self):
        """Keyboard accelerators for fullscreen and fast alignment."""
        self.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

    def _toggle_fullscreen(self):
        is_full = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not is_full)

    def _toggle_darkroom(self):
        """Toggles darkroom ambient lighting simulation."""
        self.view_eyepiece.darkroom_mode = not self.view_eyepiece.darkroom_mode
        is_dark = self.view_eyepiece.darkroom_mode
        self.darkroom_btn.configure(
            fg_color="#6366F1" if is_dark else "#334155",
            hover_color="#4F46E5" if is_dark else "#475569"
        )
        self._on_parameter_changed()

    def _toggle_sound(self):
        muted = not AudioEffects.is_muted()
        AudioEffects.set_muted(muted)
        self.sound_btn.configure(
            image=self.snd_mute_img if muted else self.snd_on_img,
            text=" Muted" if muted else " Sound",
            fg_color="#EF4444" if muted else "#10B981"
        )

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def _toggle_language(self):
        LocalizationService.toggle_language()
        is_fa = LocalizationService.is_persian()

        self.title_lbl.configure(text=LocalizationService.t("app_title"), font=FontManager.get_ui_font(14, "bold", is_fa))
        self.lang_btn.configure(text=LocalizationService.t("lang_switch"), font=FontManager.get_persian_font(11, "bold"))
        self.theme_btn.configure(text=LocalizationService.t("theme_toggle"), font=FontManager.get_ui_font(11, "bold", is_fa))
        self.darkroom_btn.configure(text=" " + LocalizationService.t("darkroom_toggle"), font=FontManager.get_ui_font(11, "bold", is_fa))

        # Re-pack header according to RTL direction
        self.title_lbl.pack_forget()
        self.title_lbl.pack(side="left" if not is_fa else "right", padx=16, pady=6)

        self._update_tabview_titles()
        self.control_panel.refresh_language()
        self.view_vernier.refresh_language()
        self.view_apparatus_3d.refresh_language()
        self.view_calculations.refresh_language()
        self.view_guide.refresh_language()
        self._on_parameter_changed()

    def _on_tab_changed(self):
        """Triggered immediately when the user clicks ANY tab in the Tabview."""
        self._on_parameter_changed()

    def _on_angle_dragged(self, new_angle: float):
        """Called when user rotates telescope arm from 2D or Eyepiece canvas."""
        self.control_panel.update_angle_externally(new_angle)
        self._on_parameter_changed()

    def _on_optic_mode_changed(self, new_mode: str):
        self.optic_mode = new_mode
        self.view_apparatus_2d.optic_mode = new_mode
        self.view_apparatus_3d.optic_mode = new_mode
        self.view_calculations.set_optic_mode(new_mode, self.prism_engine)
        self._on_parameter_changed()

    def _on_reset_all(self):
        """Resets all simulation parameters back to default state."""
        self.optic_mode = "grating"
        self.view_apparatus_2d.optic_mode = "grating"
        self.view_apparatus_3d.optic_mode = "grating"
        self.view_eyepiece.darkroom_mode = False
        self.darkroom_btn.configure(fg_color="#334155")
        self._on_parameter_changed()

    def _initial_render_all(self):
        """Pre-renders ALL views on startup so no tab is ever blank."""
        self.grating_engine.lines_per_mm = self.control_panel.current_lines_per_mm
        self.grating_engine.slit_width_mm = self.control_panel.slit_slider.get()
        self.grating_engine.oblique_incidence_deg = self.control_panel.tilt_x_slider.get() if self.error_model.params.enabled else 0.0

        source_key = self.control_panel.current_source_key
        source = SPECTRAL_SOURCES.get(source_key, SPECTRAL_SOURCES["Mercury (Hg)"])

        if self.optic_mode == "prism":
            self.current_peaks = self.prism_engine.compute_all_peaks(source)
            active_engine = self.prism_engine
        else:
            self.current_peaks = self.grating_engine.compute_all_peaks(source, max_order=3)
            active_engine = self.grating_engine

        blur_factor = self.error_model.get_focus_blur_factor()

        # Render all 6 dynamic views
        self.view_eyepiece.render_eyepiece(self.current_peaks, source)
        self.view_vernier.render_verniers()
        self.view_apparatus_2d.render_apparatus(self.current_peaks, source)
        self.view_apparatus_3d.render_3d_apparatus(self.current_peaks, source)
        self.view_profile_1d.update_profile(active_engine, source, blur_factor)
        self.view_calculations.update_live_calculations(self.grating_engine, source, self.centered_peak)
        self.metrics_panel.update_telemetry(self.centered_peak)

    # ==========================================================================
    # Unified Simulation Update Pipeline
    # ==========================================================================
    def _on_parameter_changed(self):
        """
        Recomputes physics, diffracted peaks, and updates active visual tab.
        """
        self.grating_engine.lines_per_mm = self.control_panel.current_lines_per_mm
        self.grating_engine.slit_width_mm = self.control_panel.slit_slider.get()
        self.grating_engine.oblique_incidence_deg = self.control_panel.tilt_x_slider.get() if self.error_model.params.enabled else 0.0

        source_key = self.control_panel.current_source_key
        source = SPECTRAL_SOURCES.get(source_key, SPECTRAL_SOURCES["Mercury (Hg)"])

        # Compute peaks according to active optic mode
        if self.optic_mode == "prism":
            self.current_peaks = self.prism_engine.compute_all_peaks(source)
            active_engine = self.prism_engine
        else:
            self.current_peaks = self.grating_engine.compute_all_peaks(source, max_order=3)
            active_engine = self.grating_engine

        # Detect line centered on crosshairs (+/- 0.05°)
        tele_angle = self.model.effective_telescope_angle
        self.centered_peak = None
        for p in self.current_peaks:
            is_missing = getattr(p, "is_missing_order", False)
            if not is_missing and p.intensity > 0:
                diff = (p.angle_deg - tele_angle + 180.0) % 360.0 - 180.0
                if abs(diff) <= 0.05:
                    self.centered_peak = p
                    break

        # Render Active Tab View
        active_tab = self.tabview.get()
        blur_factor = self.error_model.get_focus_blur_factor()

        if active_tab == "tab_eye":
            self.view_eyepiece.render_eyepiece(self.current_peaks, source)
        elif active_tab == "tab_vern":
            self.view_vernier.render_verniers()
        elif active_tab == "tab_2d":
            self.view_apparatus_2d.render_apparatus(self.current_peaks, source)
        elif active_tab == "tab_3d":
            self.view_apparatus_3d.render_3d_apparatus(self.current_peaks, source)
        elif active_tab == "tab_prof":
            self.view_profile_1d.update_profile(active_engine, source, blur_factor)
        elif active_tab == "tab_calc":
            self.view_calculations.update_live_calculations(self.grating_engine, source, self.centered_peak)

        # Update Telemetry Status Bar
        self.metrics_panel.update_telemetry(self.centered_peak)

    def _record_current_measurement(self):
        """Records current goniometer alignment into the laboratory observations table."""
        v1, v2 = self.model.get_vernier_readings()
        if self.centered_peak:
            line_name = self.centered_peak.line_name
            true_wl = self.centered_peak.wavelength_nm
            order = getattr(self.centered_peak, "order_m", 1)
            true_n = getattr(self.centered_peak, "refractive_index_n", None)
        else:
            line_name = "Reticle Mark"
            true_wl = 0.0
            order = 1
            true_n = None

        self.view_calculations.add_measurement_row(
            line_name=line_name,
            true_wl_nm=true_wl,
            order_m=order,
            v1=v1,
            v2=v2,
            grating_d_nm=self.grating_engine.d_nm,
            optic_mode=self.optic_mode,
            true_n=true_n
        )
        AudioEffects.play_clamp_sound()

    # ==========================================================================
    # Multi-Format Report Exports
    # ==========================================================================
    def _export_docx_report(self):
        """Exports professional Word report with native OMML equations."""
        try:
            fpath = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word Document", "*.docx")],
                initialfile="Spectrometer_Lab_Report.docx"
            )
            if not fpath:
                return

            source = SPECTRAL_SOURCES.get(self.control_panel.current_source_key, SPECTRAL_SOURCES["Mercury (Hg)"])
            DocxEquationExporter.export_report(
                filepath=fpath,
                model=self.model,
                grating_engine=self.grating_engine,
                source=source,
                measurements=self.view_calculations.measurements,
                is_persian=LocalizationService.is_persian()
            )
            messagebox.showinfo("Export Successful", f"Laboratory report saved to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Word report export error:\n{e}")

    def _export_csv_data(self):
        """Exports observations table to CSV with UTF-8 BOM."""
        try:
            fpath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Dataset", "*.csv")],
                initialfile="spectrometer_measurements.csv"
            )
            if not fpath:
                return

            ExportService.export_csv(fpath, self.view_calculations.measurements)
            messagebox.showinfo("Export Successful", f"CSV dataset saved to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"CSV export error:\n{e}")
