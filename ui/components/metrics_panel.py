"""
Bottom Telemetry & Measurement Status Panel (نوار وضعیت تله‌متری و اندازه‌گیری).
Displays real-time goniometer angles, dual Vernier scale readouts, active spectral line identification,
and experimental resolving power metrics with proper Persian font shaping.
"""

from typing import Optional, Callable, Any
import customtkinter as ctk

from physics.spectrometer_model import SpectrometerModel, VernierReading
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class MetricsPanel(ctk.CTkFrame):
    """
    Bottom telemetry strip with real-time status tiles.
    """

    def __init__(
        self,
        master,
        model: SpectrometerModel,
        on_record_click: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="#181820", corner_radius=8, height=48, **kwargs)
        self.model = model
        self.on_record_click = on_record_click

        self._create_widgets()

    def _create_widgets(self):
        is_fa = LocalizationService.is_persian()
        font_num = FontManager.get_number_font(11, "bold")
        font_sub = FontManager.get_ui_font(10, "bold", is_fa)
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)
        font_line = FontManager.get_persian_font(11, "bold") if is_fa else font_num

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Tile 1: Telescope Angle
        t1 = ctk.CTkFrame(self, fg_color="transparent")
        t1.grid(row=0, column=0, padx=6, pady=4)
        ctk.CTkLabel(t1, text=LocalizationService.t("tel_tele_angle"), font=font_sub, text_color="#94A3B8").pack(anchor="center")
        self.lbl_tele_angle = ctk.CTkLabel(t1, text="0.000°", font=font_num, text_color="#E2E8F0")
        self.lbl_tele_angle.pack(anchor="center")

        # Tile 2: Vernier 1 (V1)
        t2 = ctk.CTkFrame(self, fg_color="transparent")
        t2.grid(row=0, column=1, padx=6, pady=4)
        ctk.CTkLabel(t2, text=LocalizationService.t("tel_vernier_1"), font=font_sub, text_color="#94A3B8").pack(anchor="center")
        self.lbl_v1 = ctk.CTkLabel(t2, text="0° 00'", font=font_num, text_color="#38BDF8")
        self.lbl_v1.pack(anchor="center")

        # Tile 3: Vernier 2 (V2)
        t3 = ctk.CTkFrame(self, fg_color="transparent")
        t3.grid(row=0, column=2, padx=6, pady=4)
        ctk.CTkLabel(t3, text=LocalizationService.t("tel_vernier_2"), font=font_sub, text_color="#94A3B8").pack(anchor="center")
        self.lbl_v2 = ctk.CTkLabel(t3, text="180° 00'", font=font_num, text_color="#C084FC")
        self.lbl_v2.pack(anchor="center")

        # Tile 4: Active Centered Spectral Line (Always Vazirmatn for Persian)
        t4 = ctk.CTkFrame(self, fg_color="transparent")
        t4.grid(row=0, column=3, padx=6, pady=4)
        ctk.CTkLabel(t4, text=LocalizationService.t("tel_active_line"), font=font_sub, text_color="#94A3B8").pack(anchor="center")
        self.lbl_line = ctk.CTkLabel(t4, text=LocalizationService.t("none_detected"), font=font_line, text_color="#F59E0B")
        self.lbl_line.pack(anchor="center")

        # Tile 5: Action Record Button
        t5 = ctk.CTkFrame(self, fg_color="transparent")
        t5.grid(row=0, column=4, padx=6, pady=4)
        ctk.CTkButton(
            t5,
            text=LocalizationService.t("btn_add_measurement"),
            font=font_btn,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._on_record
        ).pack(anchor="center")

    def _on_record(self):
        if self.on_record_click:
            self.on_record_click()

    def update_telemetry(self, centered_peak: Optional[Any]):
        """Updates live readouts across the telemetry tiles."""
        is_fa = LocalizationService.is_persian()
        font_line = FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")

        tele_angle = self.model.effective_telescope_angle
        dev_angle = self.model.deviation_angle
        v1, v2 = self.model.get_vernier_readings()

        sign_str = f"+{dev_angle:.2f}°" if dev_angle > 0 else f"{dev_angle:.2f}°"
        self.lbl_tele_angle.configure(text=f"{tele_angle:.3f}° ({sign_str})")
        self.lbl_v1.configure(text=v1.readout_str)
        self.lbl_v2.configure(text=v2.readout_str)

        if centered_peak:
            if hasattr(centered_peak, "refractive_index_n"):
                info_str = f"{centered_peak.line_name} ({centered_peak.wavelength_nm:.1f}nm, n={centered_peak.refractive_index_n:.4f})"
            else:
                m_val = getattr(centered_peak, "order_m", 1)
                info_str = f"{centered_peak.line_name} ({centered_peak.wavelength_nm:.1f}nm, m={m_val})"

            self.lbl_line.configure(
                text=info_str,
                font=font_line,
                text_color=centered_peak.color_hint or "#00F0FF"
            )
        else:
            self.lbl_line.configure(
                text=LocalizationService.t("none_detected"),
                font=font_line,
                text_color="#64748B"
            )
