"""
Calculations & Lab Worksheets View (محاسبات، روابط فیزیکی و کاربرگ آزمایش).
Renders interactive theory cards with live parameter substitutions,
Balmer series Rydberg constant solver, Angle Inspector, and laboratory measurement records table.
"""

import math
from typing import List, Dict, Any, Optional, Callable
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel, VernierReading
from physics.grating_engine import GratingEngine, DiffractedPeak
from physics.constants import SpectralSource, RYDBERG_CONSTANT_H
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from utils.numeric_input import NumericInput

class CalculationsView(ctk.CTkScrollableFrame):
    """
    Scrollable calculation workspace displaying physics equations with live variable substitutions.
    """

    def __init__(
        self,
        master,
        model: SpectrometerModel,
        on_export_docx: Optional[Callable[[], None]] = None,
        on_export_csv: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.model = model
        self.on_export_docx = on_export_docx
        self.on_export_csv = on_export_csv

        # Stored experimental observations table
        self.measurements: List[Dict[str, Any]] = []

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()
        font_h = FontManager.get_ui_font(14, "bold", is_fa)
        font_sub = FontManager.get_ui_font(12, "bold", is_fa)
        font_body = FontManager.get_ui_font(11, "normal", is_fa)
        font_mono = FontManager.get_number_font(11, "bold")

        # ----------------------------------------------------------------------
        # Header & Export Actions Cluster
        # ----------------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 8))
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_txt = "روابط ریاضی، تحلیل داده‌ها و کاربرگ آزمایش اپتیک" if is_fa else "Laboratory Mathematical Models & Experimental Data Sheet"
        self.main_title_lbl = ctk.CTkLabel(self.header_frame, text=title_txt, font=font_h, text_color="#38BDF8")
        self.main_title_lbl.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=12, pady=(8, 4))

        self.btn_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.btn_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.btn_docx = ctk.CTkButton(
            self.btn_row,
            text=LocalizationService.t("btn_export_word"),
            font=font_sub,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._trigger_export_docx
        )
        self.btn_docx.pack(side="right" if is_fa else "left", padx=6)

        self.btn_csv = ctk.CTkButton(
            self.btn_row,
            text=LocalizationService.t("btn_export_csv"),
            font=font_sub,
            fg_color="#059669",
            hover_color="#047857",
            command=self._trigger_export_csv
        )
        self.btn_csv.pack(side="right" if is_fa else "left", padx=6)

        self.btn_clr = ctk.CTkButton(
            self.btn_row,
            text=LocalizationService.t("btn_clear_table"),
            font=font_sub,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.clear_measurements
        )
        self.btn_clr.pack(side="right" if is_fa else "left", padx=6)

        # ----------------------------------------------------------------------
        # Card 1: Grating Equation & Wavelength Determination
        # ----------------------------------------------------------------------
        self.card_grating = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.card_grating.grid(row=1, column=0, sticky="ew", padx=8, pady=6)
        self.card_grating.grid_columnconfigure(0, weight=1)

        c1_title = "1. Main Grating Equation (معادله اصلی توری پراش)"
        ctk.CTkLabel(self.card_grating, text=c1_title, font=font_sub, text_color="#F59E0B").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        c1_eq = "d · sin(θ_m) = m · λ    ==>    λ = (d · sin(θ_m)) / m"
        ctk.CTkLabel(self.card_grating, text=c1_eq, font=font_mono, text_color="#E2E8F0").grid(row=1, column=0, sticky="w", padx=16, pady=2)

        self.c1_sub_lbl = ctk.CTkLabel(self.card_grating, text="Live Substitution: --", font=font_mono, text_color="#38BDF8")
        self.c1_sub_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 8))

        # ----------------------------------------------------------------------
        # Card 2: Resolving Power & Angular Dispersion
        # ----------------------------------------------------------------------
        self.card_resolving = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.card_resolving.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
        self.card_resolving.grid_columnconfigure(0, weight=1)

        c2_title = "2. Resolving Power & Rayleigh Criterion (توان تفکیک و معیار ریلی)"
        ctk.CTkLabel(self.card_resolving, text=c2_title, font=font_sub, text_color="#F59E0B").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        c2_eq = "R = λ / Δλ_min = |m| · N_total      |      D = dθ / dλ = m / (d · cos θ_m)"
        ctk.CTkLabel(self.card_resolving, text=c2_eq, font=font_mono, text_color="#E2E8F0").grid(row=1, column=0, sticky="w", padx=16, pady=2)

        self.c2_sub_lbl = ctk.CTkLabel(self.card_resolving, text="Live Substitution: --", font=font_mono, text_color="#38BDF8")
        self.c2_sub_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 8))

        # ----------------------------------------------------------------------
        # Card 3: Rydberg Constant Calculation (Active on Hydrogen)
        # ----------------------------------------------------------------------
        self.card_rydberg = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.card_rydberg.grid(row=3, column=0, sticky="ew", padx=8, pady=6)
        self.card_rydberg.grid_columnconfigure(0, weight=1)

        c3_title = "3. Hydrogen Balmer Series & Rydberg Constant R_H (تعیین ثابت ریدبرگ)"
        ctk.CTkLabel(self.card_rydberg, text=c3_title, font=font_sub, text_color="#F59E0B").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        c3_eq = "1 / λ = R_H · [ 1/2² - 1/n² ]    ==>    R_H = 1 / [ λ · (0.25 - 1/n²) ]"
        ctk.CTkLabel(self.card_rydberg, text=c3_eq, font=font_mono, text_color="#E2E8F0").grid(row=1, column=0, sticky="w", padx=16, pady=2)

        self.c3_sub_lbl = ctk.CTkLabel(self.card_rydberg, text="Balmer Evaluation: --", font=font_mono, text_color="#10B981")
        self.c3_sub_lbl.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 8))

        # ----------------------------------------------------------------------
        # Card 4: Laboratory Recorded Observations Table
        # ----------------------------------------------------------------------
        self.card_table = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.card_table.grid(row=4, column=0, sticky="ew", padx=8, pady=6)
        self.card_table.grid_columnconfigure(0, weight=1)

        c4_title = "4. Recorded Experimental Measurements Table (جدول اندازه‌گیری‌های ثبت‌شده)"
        ctk.CTkLabel(self.card_table, text=c4_title, font=font_sub, text_color="#F59E0B").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        self.table_content_frame = ctk.CTkFrame(self.card_table, fg_color="transparent")
        self.table_content_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.render_measurements_table()

    def refresh_language(self):
        """Updates titles and button labels on language toggle."""
        is_fa = LocalizationService.is_persian()
        font_h = FontManager.get_ui_font(14, "bold", is_fa)
        font_sub = FontManager.get_ui_font(12, "bold", is_fa)

        title_txt = "روابط ریاضی، تحلیل داده‌ها و کاربرگ آزمایش اپتیک" if is_fa else "Laboratory Mathematical Models & Experimental Data Sheet"
        self.main_title_lbl.configure(text=title_txt, font=font_h)
        self.btn_docx.configure(text=LocalizationService.t("btn_export_word"), font=font_sub)
        self.btn_csv.configure(text=LocalizationService.t("btn_export_csv"), font=font_sub)
        self.btn_clr.configure(text=LocalizationService.t("btn_clear_table"), font=font_sub)
        self.render_measurements_table()

    def _trigger_export_docx(self):
        if self.on_export_docx:
            self.on_export_docx()

    def _trigger_export_csv(self):
        if self.on_export_csv:
            self.on_export_csv()

    def add_measurement_row(
        self,
        line_name: str,
        true_wl_nm: float,
        order_m: int,
        v1: VernierReading,
        v2: VernierReading,
        grating_d_nm: float
    ):
        """Records current goniometer alignment into the laboratory observations table."""
        # Calculate corrected angle
        corr_deg = self.model.get_corrected_angle_from_verniers(v1, v2)
        dev_deg = abs((corr_deg + 180.0) % 360.0 - 180.0)

        # Calculate experimental wavelength: λ = d * sin(θ) / |m|
        if order_m != 0:
            calc_wl_nm = (grating_d_nm * math.sin(math.radians(dev_deg))) / abs(order_m)
            err_percent = abs(calc_wl_nm - true_wl_nm) / true_wl_nm * 100.0 if true_wl_nm > 0 else 0.0
        else:
            calc_wl_nm = 0.0
            err_percent = 0.0

        row_data = {
            "index": len(self.measurements) + 1,
            "line_name": line_name,
            "order_m": order_m,
            "v1_str": v1.readout_str,
            "v2_str": v2.readout_str,
            "corr_deg": corr_deg,
            "dev_deg": dev_deg,
            "true_wl_nm": true_wl_nm,
            "calc_wl_nm": calc_wl_nm,
            "error_percent": err_percent
        }
        self.measurements.append(row_data)
        self.render_measurements_table()

    def clear_measurements(self):
        self.measurements.clear()
        self.render_measurements_table()

    def render_measurements_table(self):
        """Rebuilds the table rows in the UI."""
        for child in self.table_content_frame.winfo_children():
            child.destroy()

        font_header = FontManager.get_number_font(10, "bold")
        font_row = FontManager.get_number_font(9, "normal")

        # Table Header
        headers = ["#", "Line Name", "Order m", "Vernier 1", "Vernier 2", "θ (dev)", "λ Calc (nm)", "λ True (nm)", "Error %"]
        col_widths = [30, 110, 60, 90, 90, 80, 90, 90, 70]

        h_frame = ctk.CTkFrame(self.table_content_frame, fg_color="#272732", height=26)
        h_frame.pack(fill="x", pady=1)

        for i, (h, w) in enumerate(zip(headers, col_widths)):
            lbl = ctk.CTkLabel(h_frame, text=h, font=font_header, width=w, anchor="center")
            lbl.pack(side="left", padx=2)

        if not self.measurements:
            empty_lbl = ctk.CTkLabel(
                self.table_content_frame,
                text="[No readings recorded yet. Center a line on the reticle and click 'Record Current Angle']",
                font=FontManager.get_number_font(10),
                text_color="#64748B"
            )
            empty_lbl.pack(pady=10)
            return

        for row in self.measurements:
            r_frame = ctk.CTkFrame(self.table_content_frame, fg_color="#1E1E26", height=24)
            r_frame.pack(fill="x", pady=1)

            vals = [
                str(row["index"]),
                row["line_name"],
                f"m={row['order_m']}",
                row["v1_str"],
                row["v2_str"],
                f"{row['dev_deg']:.2f}°",
                f"{row['calc_wl_nm']:.2f}",
                f"{row['true_wl_nm']:.2f}",
                f"{row['error_percent']:.2f}%"
            ]

            for val, w in zip(vals, col_widths):
                lbl = ctk.CTkLabel(r_frame, text=val, font=font_row, width=w, anchor="center")
                lbl.pack(side="left", padx=2)

    def update_live_calculations(
        self,
        grating_engine: GratingEngine,
        source: SpectralSource,
        closest_peak: Optional[DiffractedPeak]
    ):
        """Updates live substitutions in mathematical cards."""
        tele_angle = self.model.effective_telescope_angle
        dev_angle = self.model.deviation_angle
        d_nm = grating_engine.d_nm

        # Card 1 Update
        if closest_peak:
            if hasattr(closest_peak, "order_m") and closest_peak.order_m != 0:
                calc_wl = (d_nm * math.sin(math.radians(abs(dev_angle)))) / abs(closest_peak.order_m)
                self.c1_sub_lbl.configure(
                    text=f"Line: {closest_peak.line_name} | d = {d_nm:.2f} nm, θ = {dev_angle:.3f}°, m = {closest_peak.order_m} ==> λ_calc = {calc_wl:.2f} nm (True: {closest_peak.wavelength_nm:.2f} nm)"
                )
            elif hasattr(closest_peak, "refractive_index_n"):
                n_calc = math.sin(math.radians((60.0 + abs(dev_angle)) / 2.0)) / math.sin(math.radians(30.0))
                self.c1_sub_lbl.configure(
                    text=f"Prism Refraction: {closest_peak.line_name} | D_min = {abs(dev_angle):.3f}° ==> n_exp = {n_calc:.4f} (True n: {closest_peak.refractive_index_n:.4f})"
                )
            else:
                self.c1_sub_lbl.configure(text=f"Current: d = {d_nm:.2f} nm, θ_dev = {dev_angle:.3f}°")
        else:
            self.c1_sub_lbl.configure(text=f"Current: d = {d_nm:.2f} nm, θ_dev = {dev_angle:.3f}°")

        # Card 2 Update
        n_t = grating_engine.illuminated_lines_Nt
        order_factor = abs(closest_peak.order_m) if closest_peak else 1
        r_power = n_t * order_factor
        min_dlambda_str = f"{(550.0 / r_power):.3f} nm" if r_power > 0 else "N/A (Order 0)"
        self.c2_sub_lbl.configure(
            text=f"Illuminated Grooves N_t = {n_t:.0f} | Resolving Power R = {r_power:.0f} | Min Δλ = {min_dlambda_str} at 550nm"
        )

        # Card 3 Update (Hydrogen Balmer)
        if source.id == "H" and closest_peak and closest_peak.n_upper:
            rydberg_res = grating_engine.calculate_rydberg_constant(
                dev_angle, closest_peak.order_m, grating_engine.d_m, closest_peak.n_upper
            )
            r_exp = rydberg_res["R_H_exp"]
            err_p = rydberg_res["rel_error_percent"]
            self.c3_sub_lbl.configure(
                text=f"Line: {closest_peak.line_name} (n={closest_peak.n_upper}) ==> R_H(exp) = {r_exp:.4e} m⁻¹ (True: {RYDBERG_CONSTANT_H:.4e} m⁻¹, Error: {err_p:.2f}%)"
            )
        else:
            self.c3_sub_lbl.configure(
                text="Hydrogen Balmer Solver: Select 'Hydrogen (H)' source to compute experimental Rydberg constant R_H."
            )
