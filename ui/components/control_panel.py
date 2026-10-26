"""
Interactive Spectrometer Control Panel (پنل کنترل آزمایشگاه و تنظیمات گونیومتر).
Manages spectral lamp selection (Persian & English), dispersive element mode (Grating vs Prism),
clamp/fine-tangent mechanics, optical focus knobs, reset parameters action, and mystery element quiz.
"""

from typing import Callable, Optional, Dict, Any, List
import customtkinter as ctk

from physics.constants import SPECTRAL_SOURCES, GRATING_PRESETS, PRISM_PRESETS, SpectralSource, SpectralLine
from physics.spectrometer_model import SpectrometerModel
from physics.error_model import SpectrometerErrorModel
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.numeric_input import NumericInput
from utils.audio_effects import AudioEffects
from ui.components.custom_line_dialog import CustomLineDialog
from ui.components.unknown_element_dialog import UnknownElementDialog

class ControlPanel(ctk.CTkScrollableFrame):
    """
    Sidebar control frame with intuitive mechanical controls, sliders, and options.
    """

    def __init__(
        self,
        master,
        model: SpectrometerModel,
        error_model: SpectrometerErrorModel,
        on_change: Callable[[], None],
        on_record_measurement: Callable[[], None],
        on_reset_all: Optional[Callable[[], None]] = None,
        on_optic_mode_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.model = model
        self.error_model = error_model
        self.on_change = on_change
        self.on_record_measurement = on_record_measurement
        self.on_reset_all = on_reset_all
        self.on_optic_mode_change = on_optic_mode_change

        self.optic_mode = "grating" # "grating" or "prism"
        self.current_source_key = "Mercury (Hg)"
        self.current_grating_key = "600 lines/mm"
        self.current_lines_per_mm = 600.0

        self._create_widgets()

    def _get_lamp_display_names(self) -> List[str]:
        """Returns localized display names for spectral lamps matching current language."""
        is_fa = LocalizationService.is_persian()
        return [
            src.name_fa if is_fa else src.name_en
            for src in SPECTRAL_SOURCES.values()
        ]

    def _get_key_from_display_name(self, display_name: str) -> str:
        for k, src in SPECTRAL_SOURCES.items():
            if src.name_fa == display_name or src.name_en == display_name or k == display_name:
                return k
        return "Mercury (Hg)"

    def _get_display_name_from_key(self, key: str) -> str:
        src = SPECTRAL_SOURCES.get(key)
        if not src:
            return key
        return src.name_fa if LocalizationService.is_persian() else src.name_en

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()
        font_sec = FontManager.get_ui_font(12, "bold", is_fa)
        font_lbl = FontManager.get_ui_font(11, "bold", is_fa)
        font_num = FontManager.get_number_font(11, "bold")
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)

        # ======================================================================
        # SECTION 1: Dispersive Element (Grating vs Prism) & Light Source
        # ======================================================================
        self.sec1 = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.sec1.pack(fill="x", padx=6, pady=4)
        self.sec1.grid_columnconfigure(0, weight=1)

        self.lbl_sec1 = ctk.CTkLabel(self.sec1, text=LocalizationService.t("panel_sources"), font=font_sec, text_color="#38BDF8")
        self.lbl_sec1.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=10, pady=(6, 4))

        # Dispersive Optic Mode Selector (Grating vs Prism)
        self.lbl_optic_mode = ctk.CTkLabel(self.sec1, text=LocalizationService.t("optic_mode_label"), font=font_lbl)
        self.lbl_optic_mode.grid(row=1, column=0, sticky="e" if is_fa else "w", padx=10, pady=(1, 1))

        self.optic_segmented = ctk.CTkSegmentedButton(
            self.sec1,
            values=[
                LocalizationService.t("optic_grating"),
                LocalizationService.t("optic_prism")
            ],
            font=font_btn,
            command=self._on_segmented_optic_change
        )
        self.optic_segmented.set(LocalizationService.t("optic_grating"))
        self.optic_segmented.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 6))

        # Lamp Source Dropdown (Localized) & Buttons
        self.lbl_lamp = ctk.CTkLabel(self.sec1, text=LocalizationService.t("lbl_lamp"), font=font_lbl)
        self.lbl_lamp.grid(row=3, column=0, sticky="e" if is_fa else "w", padx=10, pady=(2, 1))

        lamp_row = ctk.CTkFrame(self.sec1, fg_color="transparent")
        lamp_row.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 4))

        lamp_displays = self._get_lamp_display_names()
        self.lamp_menu = ctk.CTkOptionMenu(
            lamp_row,
            values=lamp_displays,
            font=FontManager.get_persian_font(11, "bold") if is_fa else font_num,
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            command=self._on_lamp_change
        )
        self.lamp_menu.set(self._get_display_name_from_key(self.current_source_key))
        self.lamp_menu.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_custom_line = ctk.CTkButton(
            lamp_row,
            text=LocalizationService.t("lbl_custom_btn"),
            font=font_btn,
            width=70,
            command=self._open_custom_line_dialog
        )
        self.btn_custom_line.pack(side="right")

        # Diffraction Grating / Prism Specifier
        self.lbl_grating = ctk.CTkLabel(self.sec1, text=LocalizationService.t("lbl_grating"), font=font_lbl)
        self.lbl_grating.grid(row=5, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        grating_options = list(GRATING_PRESETS.keys())
        self.grating_menu = ctk.CTkOptionMenu(
            self.sec1,
            values=grating_options,
            font=font_num,
            command=self._on_grating_change
        )
        self.grating_menu.set(self.current_grating_key)
        self.grating_menu.grid(row=6, column=0, sticky="ew", padx=8, pady=(0, 2))

        # Grating / Prism Constant Readout
        self.d_constant_lbl = ctk.CTkLabel(
            self.sec1,
            text="d = 1666.67 nm  (1.667 µm)",
            font=font_num,
            text_color="#F59E0B"
        )
        self.d_constant_lbl.grid(row=7, column=0, sticky="e" if is_fa else "w", padx=10, pady=(1, 4))

        # Unknown Element Quiz Action Button
        self.btn_quiz = ctk.CTkButton(
            self.sec1,
            text=LocalizationService.t("btn_blind_quiz"),
            font=font_btn,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self._open_unknown_element_dialog
        )
        self.btn_quiz.grid(row=8, column=0, sticky="ew", padx=8, pady=(2, 6))

        # ======================================================================
        # SECTION 2: Telescope & Goniometer Rotation Controls
        # ======================================================================
        self.sec2 = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.sec2.pack(fill="x", padx=6, pady=4)
        self.sec2.grid_columnconfigure(0, weight=1)

        self.lbl_sec2 = ctk.CTkLabel(self.sec2, text=LocalizationService.t("panel_mechanics"), font=font_sec, text_color="#38BDF8")
        self.lbl_sec2.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=10, pady=(6, 4))

        # Clamp Screw Toggle Button
        clamp_row = ctk.CTkFrame(self.sec2, fg_color="transparent")
        clamp_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 4))

        self.lbl_clamp = ctk.CTkLabel(clamp_row, text=LocalizationService.t("lbl_clamp"), font=font_lbl)
        self.lbl_clamp.pack(side="right" if is_fa else "left", padx=4)

        self.btn_clamp = ctk.CTkButton(
            clamp_row,
            text=LocalizationService.t("btn_clamp_free"),
            font=font_btn,
            fg_color="#059669",
            hover_color="#047857",
            command=self._on_toggle_clamp
        )
        self.btn_clamp.pack(side="left" if is_fa else "right", fill="x", expand=True, padx=4)

        # Coarse Angle Slider & Entry
        self.lbl_coarse = ctk.CTkLabel(self.sec2, text=LocalizationService.t("lbl_coarse_angle"), font=font_lbl)
        self.lbl_coarse.grid(row=2, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        coarse_row = ctk.CTkFrame(self.sec2, fg_color="transparent")
        coarse_row.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 2))

        self.coarse_slider = ctk.CTkSlider(
            coarse_row,
            from_=0.0,
            to=360.0,
            number_of_steps=720,
            command=self._on_coarse_slider_change
        )
        self.coarse_slider.set(self.model.effective_telescope_angle)
        self.coarse_slider.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.coarse_entry = ctk.CTkEntry(coarse_row, width=64, font=font_num)
        self.coarse_entry.insert(0, f"{self.model.effective_telescope_angle:.1f}°")
        self.coarse_entry.pack(side="right")
        self.coarse_entry.bind("<Return>", self._on_coarse_entry_submit)

        # Fine Tangent Micrometer Screw (Active when clamped)
        self.lbl_fine = ctk.CTkLabel(self.sec2, text=LocalizationService.t("lbl_fine_tangent"), font=font_lbl)
        self.lbl_fine.grid(row=4, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        fine_row = ctk.CTkFrame(self.sec2, fg_color="transparent")
        fine_row.grid(row=5, column=0, sticky="ew", padx=8, pady=(0, 4))

        ctk.CTkButton(fine_row, text="◀ -1'", width=42, font=font_num, command=lambda: self._step_fine_tangent(-1.0/60.0)).pack(side="left", padx=1)
        self.fine_slider = ctk.CTkSlider(
            fine_row,
            from_=-5.0,
            to=5.0,
            number_of_steps=1200,
            command=self._on_fine_slider_change
        )
        self.fine_slider.set(0.0)
        self.fine_slider.pack(side="left", fill="x", expand=True, padx=4)
        ctk.CTkButton(fine_row, text="+1' ▶", width=42, font=font_num, command=lambda: self._step_fine_tangent(1.0/60.0)).pack(side="right", padx=1)

        # Helper Actions Row (Center 0° & Record Measurement)
        action_row = ctk.CTkFrame(self.sec2, fg_color="transparent")
        action_row.grid(row=6, column=0, sticky="ew", padx=8, pady=(4, 6))

        self.btn_zero = ctk.CTkButton(
            action_row,
            text=LocalizationService.t("btn_center_zero"),
            font=font_btn,
            fg_color="#475569",
            hover_color="#334155",
            command=self._align_center_zero
        )
        self.btn_zero.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_record = ctk.CTkButton(
            action_row,
            text=LocalizationService.t("btn_add_measurement"),
            font=font_btn,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self.on_record_measurement
        )
        self.btn_record.pack(side="right", expand=True, fill="x", padx=2)

        # Reset All Parameters Button
        self.btn_reset = ctk.CTkButton(
            self.sec2,
            text=LocalizationService.t("btn_reset_params"),
            font=font_btn,
            fg_color="#EA580C",
            hover_color="#C2410C",
            command=self._reset_all_parameters
        )
        self.btn_reset.grid(row=7, column=0, sticky="ew", padx=8, pady=(0, 6))

        # Update initial clamp state
        self._sync_clamp_ui_state()

        # ======================================================================
        # SECTION 3: Optics & Alignment Knobs
        # ======================================================================
        self.sec3 = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.sec3.pack(fill="x", padx=6, pady=4)
        self.sec3.grid_columnconfigure(0, weight=1)

        self.lbl_sec3 = ctk.CTkLabel(self.sec3, text=LocalizationService.t("panel_optics"), font=font_sec, text_color="#38BDF8")
        self.lbl_sec3.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=10, pady=(6, 4))

        # Entrance Slit Width
        self.lbl_slit = ctk.CTkLabel(self.sec3, text=LocalizationService.t("lbl_slit_width"), font=font_lbl)
        self.lbl_slit.grid(row=1, column=0, sticky="e" if is_fa else "w", padx=10, pady=(2, 1))

        slit_row = ctk.CTkFrame(self.sec3, fg_color="transparent")
        slit_row.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 2))
        self.slit_slider = ctk.CTkSlider(slit_row, from_=0.0, to=0.50, number_of_steps=50, command=self._on_slit_change)
        self.slit_slider.set(0.05)
        self.slit_slider.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.slit_lbl = ctk.CTkLabel(slit_row, text="0.05 mm", font=font_num, width=54)
        self.slit_lbl.pack(side="right")

        # Telescope Focus Knob
        self.lbl_tele_f = ctk.CTkLabel(self.sec3, text=LocalizationService.t("lbl_tele_focus"), font=font_lbl)
        self.lbl_tele_f.grid(row=3, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        tele_f_row = ctk.CTkFrame(self.sec3, fg_color="transparent")
        tele_f_row.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 2))
        self.tele_focus_slider = ctk.CTkSlider(tele_f_row, from_=0.0, to=100.0, command=self._on_focus_change)
        self.tele_focus_slider.set(50.0)
        self.tele_focus_slider.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.tele_focus_lbl = ctk.CTkLabel(tele_f_row, text="50%", font=font_num, width=54)
        self.tele_focus_lbl.pack(side="right")

        # Collimator Focus Knob
        self.lbl_coll_f = ctk.CTkLabel(self.sec3, text=LocalizationService.t("lbl_coll_focus"), font=font_lbl)
        self.lbl_coll_f.grid(row=5, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        coll_f_row = ctk.CTkFrame(self.sec3, fg_color="transparent")
        coll_f_row.grid(row=6, column=0, sticky="ew", padx=8, pady=(0, 4))
        self.coll_focus_slider = ctk.CTkSlider(coll_f_row, from_=0.0, to=100.0, command=self._on_focus_change)
        self.coll_focus_slider.set(50.0)
        self.coll_focus_slider.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.coll_focus_lbl = ctk.CTkLabel(coll_f_row, text="50%", font=font_num, width=54)
        self.coll_focus_lbl.pack(side="right")

        # ======================================================================
        # SECTION 4: Systematic Errors (Toggleable)
        # ======================================================================
        self.sec4 = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.sec4.pack(fill="x", padx=6, pady=4)
        self.sec4.grid_columnconfigure(0, weight=1)

        self.sw_errors = ctk.CTkSwitch(
            self.sec4,
            text=LocalizationService.t("sw_enable_errors"),
            font=font_sec,
            command=self._on_toggle_errors
        )
        self.sw_errors.select()
        self.sw_errors.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=10, pady=6)

        # Table Leveling Pitch & Roll Tilt Sliders (Schuster Method)
        self.lbl_tilt = ctk.CTkLabel(self.sec4, text=LocalizationService.t("lbl_table_tilt"), font=font_lbl)
        self.lbl_tilt.grid(row=1, column=0, sticky="e" if is_fa else "w", padx=10, pady=(2, 1))

        tilt_row = ctk.CTkFrame(self.sec4, fg_color="transparent")
        tilt_row.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 2))
        self.tilt_x_slider = ctk.CTkSlider(tilt_row, from_=-0.8, to=0.8, command=self._on_tilt_change)
        self.tilt_x_slider.set(0.0)
        self.tilt_x_slider.pack(fill="x", pady=1)

        # Eccentricity Axis Offset
        self.lbl_ecc = ctk.CTkLabel(self.sec4, text=LocalizationService.t("lbl_eccentricity"), font=font_lbl)
        self.lbl_ecc.grid(row=3, column=0, sticky="e" if is_fa else "w", padx=10, pady=(4, 1))

        ecc_row = ctk.CTkFrame(self.sec4, fg_color="transparent")
        ecc_row.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 6))
        self.ecc_slider = ctk.CTkSlider(ecc_row, from_=0.0, to=40.0, command=self._on_ecc_change)
        self.ecc_slider.set(15.0)
        self.ecc_slider.pack(fill="x", pady=1)

    def refresh_language(self):
        """Updates all section titles, labels, and buttons for active language."""
        is_fa = LocalizationService.is_persian()
        font_sec = FontManager.get_ui_font(12, "bold", is_fa)
        font_lbl = FontManager.get_ui_font(11, "bold", is_fa)
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)

        self.lbl_sec1.configure(text=LocalizationService.t("panel_sources"), font=font_sec)
        self.lbl_optic_mode.configure(text=LocalizationService.t("optic_mode_label"), font=font_lbl)
        self.optic_segmented.configure(
            values=[LocalizationService.t("optic_grating"), LocalizationService.t("optic_prism")],
            font=font_btn
        )
        current_optic_str = LocalizationService.t("optic_grating") if self.optic_mode == "grating" else LocalizationService.t("optic_prism")
        self.optic_segmented.set(current_optic_str)

        self.lbl_lamp.configure(text=LocalizationService.t("lbl_lamp"), font=font_lbl)
        lamp_displays = self._get_lamp_display_names()
        self.lamp_menu.configure(
            values=lamp_displays,
            font=font_btn if is_fa else FontManager.get_number_font(11, "bold"),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11)
        )
        self.lamp_menu.set(self._get_display_name_from_key(self.current_source_key))
        self.btn_custom_line.configure(text=LocalizationService.t("lbl_custom_btn"), font=font_btn)
        self.btn_quiz.configure(text=LocalizationService.t("btn_blind_quiz"), font=font_btn)

        optic_spec_lbl = LocalizationService.t("lbl_grating") if self.optic_mode == "grating" else ("مشخصات منشور:" if is_fa else "Prism Material:")
        self.lbl_grating.configure(text=optic_spec_lbl, font=font_lbl)

        self.lbl_sec2.configure(text=LocalizationService.t("panel_mechanics"), font=font_sec)
        self.lbl_clamp.configure(text=LocalizationService.t("lbl_clamp"), font=font_lbl)
        self.lbl_coarse.configure(text=LocalizationService.t("lbl_coarse_angle"), font=font_lbl)
        self.lbl_fine.configure(text=LocalizationService.t("lbl_fine_tangent"), font=font_lbl)
        self.btn_zero.configure(text=LocalizationService.t("btn_center_zero"), font=font_btn)
        self.btn_record.configure(text=LocalizationService.t("btn_add_measurement"), font=font_btn)
        self.btn_reset.configure(text=LocalizationService.t("btn_reset_params"), font=font_btn)

        self.lbl_sec3.configure(text=LocalizationService.t("panel_optics"), font=font_sec)
        self.lbl_slit.configure(text=LocalizationService.t("lbl_slit_width"), font=font_lbl)
        self.lbl_tele_f.configure(text=LocalizationService.t("lbl_tele_focus"), font=font_lbl)
        self.lbl_coll_f.configure(text=LocalizationService.t("lbl_coll_focus"), font=font_lbl)

        self.sw_errors.configure(text=LocalizationService.t("sw_enable_errors"), font=font_sec)
        self.lbl_tilt.configure(text=LocalizationService.t("lbl_table_tilt"), font=font_lbl)
        self.lbl_ecc.configure(text=LocalizationService.t("lbl_eccentricity"), font=font_lbl)

        self._sync_clamp_ui_state()

    # ==========================================================================
    # Handlers & Synchronization
    # ==========================================================================
    def _on_segmented_optic_change(self, value: str):
        is_prism = (value == LocalizationService.t("optic_prism") or "Prism" in value or "منشور" in value)
        self.optic_mode = "prism" if is_prism else "grating"

        is_fa = LocalizationService.is_persian()
        if self.optic_mode == "prism":
            self.lbl_grating.configure(text="مشخصات منشور شیشه‌ای:" if is_fa else "Prism Glass Material:")
            prism_options = list(PRISM_PRESETS.keys())
            self.grating_menu.configure(values=prism_options)
            self.grating_menu.set(prism_options[0])
            p_spec = PRISM_PRESETS[prism_options[0]]
            self.d_constant_lbl.configure(text=f"A = {p_spec['apex_angle_deg']:.0f}° | n_D ≈ 1.65")
        else:
            self.lbl_grating.configure(text=LocalizationService.t("lbl_grating"))
            grating_options = list(GRATING_PRESETS.keys())
            self.grating_menu.configure(values=grating_options)
            self.grating_menu.set(self.current_grating_key)
            preset = GRATING_PRESETS[self.current_grating_key]
            self.d_constant_lbl.configure(text=f"d = {preset['d_nm']:.2f} nm  ({(preset['d_nm']*1e-3):.3f} µm)")

        if self.on_optic_mode_change:
            self.on_optic_mode_change(self.optic_mode)
        self.on_change()

    def _on_lamp_change(self, choice: str):
        self.current_source_key = self._get_key_from_display_name(choice)
        self.on_change()

    def _on_grating_change(self, choice: str):
        if self.optic_mode == "grating":
            self.current_grating_key = choice
            preset = GRATING_PRESETS.get(choice)
            if preset:
                self.current_lines_per_mm = preset["n_lines_per_mm"]
                self.d_constant_lbl.configure(text=f"d = {preset['d_nm']:.2f} nm  ({(preset['d_nm']*1e-3):.3f} µm)")
        else:
            p_spec = PRISM_PRESETS.get(choice)
            if p_spec:
                self.d_constant_lbl.configure(text=f"A = {p_spec['apex_angle_deg']:.0f}° | n_D ≈ 1.65")
        self.on_change()

    def _open_custom_line_dialog(self):
        def _add_line_cb(line: SpectralLine):
            custom_source = SPECTRAL_SOURCES.get("Custom (User Defined)")
            if custom_source:
                custom_source.lines.append(line)
                self.current_source_key = "Custom (User Defined)"
                self.lamp_menu.set(self._get_display_name_from_key(self.current_source_key))
                self.on_change()
        CustomLineDialog(self.winfo_toplevel(), on_add=_add_line_cb)

    def _open_unknown_element_dialog(self):
        UnknownElementDialog(self.winfo_toplevel(), current_source_key=self.current_source_key)

    def _reset_all_parameters(self):
        """Resets all mechanical, optical, and error parameters to default state."""
        if self.model.is_clamped:
            self.model.toggle_clamp()

        self.model.set_coarse_angle(0.0)
        self.model.fine_tangent_angle_deg = 0.0
        self.coarse_slider.set(0.0)
        self.coarse_entry.delete(0, "end")
        self.coarse_entry.insert(0, "0.0°")
        self.fine_slider.set(0.0)

        self.slit_slider.set(0.05)
        self.slit_lbl.configure(text="0.05 mm")
        self.tele_focus_slider.set(50.0)
        self.tele_focus_lbl.configure(text="50%")
        self.coll_focus_slider.set(50.0)
        self.coll_focus_lbl.configure(text="50%")

        self.tilt_x_slider.set(0.0)
        self.ecc_slider.set(15.0)

        self.error_model.params.collimator_focus_percent = 50.0
        self.error_model.params.telescope_focus_percent = 50.0
        self.error_model.params.table_tilt_x_deg = 0.0
        self.error_model.params.table_tilt_y_deg = 0.0
        self.error_model.params.oblique_incidence_deg = 0.0
        self.error_model.params.eccentricity_um = 15.0

        self.current_source_key = "Mercury (Hg)"
        self.lamp_menu.set(self._get_display_name_from_key("Mercury (Hg)"))

        self.optic_mode = "grating"
        self.optic_segmented.set(LocalizationService.t("optic_grating"))
        self.current_grating_key = "600 lines/mm"
        self.current_lines_per_mm = 600.0
        preset = GRATING_PRESETS["600 lines/mm"]
        self.d_constant_lbl.configure(text=f"d = {preset['d_nm']:.2f} nm  ({(preset['d_nm']*1e-3):.3f} µm)")

        self._sync_clamp_ui_state()
        AudioEffects.play_clamp_sound()

        if self.on_reset_all:
            self.on_reset_all()
        self.on_change()

    def _on_toggle_clamp(self):
        is_locked = self.model.toggle_clamp()
        AudioEffects.play_clamp_sound()
        self._sync_clamp_ui_state()
        self.on_change()

    def _sync_clamp_ui_state(self):
        if self.model.is_clamped:
            self.btn_clamp.configure(
                text=LocalizationService.t("btn_clamp_locked"),
                fg_color="#DC2626", hover_color="#B91C1C"
            )
            self.coarse_slider.configure(state="disabled")
            self.fine_slider.configure(state="normal")
            self.fine_slider.set(self.model.fine_tangent_angle_deg)
        else:
            self.btn_clamp.configure(
                text=LocalizationService.t("btn_clamp_free"),
                fg_color="#059669", hover_color="#047857"
            )
            self.coarse_slider.configure(state="normal")
            self.fine_slider.configure(state="disabled")
            self.coarse_slider.set(self.model.effective_telescope_angle)

    def _on_coarse_slider_change(self, val: float):
        if not self.model.is_clamped:
            self.model.set_coarse_angle(val)
            self.coarse_entry.delete(0, "end")
            self.coarse_entry.insert(0, f"{val:.1f}°")
            self.on_change()

    def _on_coarse_entry_submit(self, event=None):
        if not self.model.is_clamped:
            val = NumericInput.parse_float(self.coarse_entry.get(), default=0.0, min_val=0.0, max_val=360.0)
            self.model.set_coarse_angle(val)
            self.coarse_slider.set(val)
            self.on_change()

    def _on_fine_slider_change(self, val: float):
        if self.model.is_clamped:
            self.model.set_fine_tangent(val)
            AudioEffects.play_tangent_click()
            self.on_change()

    def _step_fine_tangent(self, step_deg: float):
        if self.model.is_clamped:
            new_val = self.model.fine_tangent_angle_deg + step_deg
            self.model.set_fine_tangent(new_val)
            self.fine_slider.set(self.model.fine_tangent_angle_deg)
            AudioEffects.play_tangent_click()
            self.on_change()

    def _align_center_zero(self):
        """Aligns telescope directly with the zero-order straight beam."""
        if self.model.is_clamped:
            self.model.toggle_clamp()
            self._sync_clamp_ui_state()
        self.model.set_coarse_angle(0.0)
        self.coarse_slider.set(0.0)
        self.coarse_entry.delete(0, "end")
        self.coarse_entry.insert(0, "0.0°")
        self.on_change()

    def _on_slit_change(self, val: float):
        self.slit_lbl.configure(text=f"{val:.2f} mm")
        self.on_change()

    def _on_focus_change(self, val: float):
        self.tele_focus_lbl.configure(text=f"{self.tele_focus_slider.get():.0f}%")
        self.coll_focus_lbl.configure(text=f"{self.coll_focus_slider.get():.0f}%")
        self.error_model.params.telescope_focus_percent = self.tele_focus_slider.get()
        self.error_model.params.collimator_focus_percent = self.coll_focus_slider.get()
        self.on_change()

    def _on_toggle_errors(self):
        self.error_model.params.enabled = (self.sw_errors.get() == 1)
        self.model.enable_eccentricity = self.error_model.params.enabled
        self.on_change()

    def _on_tilt_change(self, val: float):
        self.error_model.params.table_tilt_x_deg = val
        self.on_change()

    def _on_ecc_change(self, val: float):
        self.error_model.params.eccentricity_um = val
        self.model.eccentricity_um = val
        self.on_change()

    def update_angle_externally(self, new_angle: float):
        """Called when angle is updated from 2D/Eyepiece canvas drag."""
        if not self.model.is_clamped:
            self.coarse_slider.set(new_angle)
            self.coarse_entry.delete(0, "end")
            self.coarse_entry.insert(0, f"{new_angle:.1f}°")
        else:
            self.fine_slider.set(self.model.fine_tangent_angle_deg)
