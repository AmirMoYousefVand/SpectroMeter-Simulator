"""
Custom Spectral Emission Line Dialog.
Allows user to define custom emission wavelengths and intensities.
"""

from typing import Callable, Optional
import customtkinter as ctk

from physics.constants import SpectralLine
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.numeric_input import NumericInput
from utils.resource_utils import apply_window_icon

class CustomLineDialog(ctk.CTkToplevel):
    """Modal dialog for creating and inserting custom spectral lines."""

    def __init__(self, master, on_add: Callable[[SpectralLine], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_add = on_add

        is_fa = LocalizationService.is_persian()
        self.title("افزودن خط طیفی سفارشی" if is_fa else "Add Custom Spectral Line")
        self.geometry("400x350")
        self.resizable(False, False)
        self.grab_set()

        apply_window_icon(self)
        self._create_widgets()

    def _create_widgets(self):
        is_fa = LocalizationService.is_persian()
        font_lbl = FontManager.get_ui_font(12, "bold", is_fa)
        font_entry = FontManager.get_number_font(12, "normal")
        font_btn = FontManager.get_ui_font(12, "bold", is_fa)

        self.grid_columnconfigure(0, weight=1)

        # Title
        t_text = "تعریف خط طیفی گسیلی جدید" if is_fa else "Define Custom Emission Line"
        ctk.CTkLabel(self, text=t_text, font=FontManager.get_ui_font(14, "bold", is_fa), text_color="#38BDF8").pack(pady=(16, 12))

        # Line Name
        name_lbl = "نام خط طیفی:" if is_fa else "Line Name / Identifier:"
        ctk.CTkLabel(self, text=name_lbl, font=font_lbl).pack(anchor="e" if is_fa else "w", padx=24, pady=(4, 2))
        self.entry_name = ctk.CTkEntry(self, font=font_entry, placeholder_text="e.g. Laser Peak")
        self.entry_name.insert(0, "Custom 580nm")
        self.entry_name.pack(fill="x", padx=24, pady=(0, 8))

        # Wavelength (nm)
        wl_lbl = "طول‌موج (نانومتر) [۳۸۰ تا ۷۸۰]:" if is_fa else "Wavelength (nm) [380.0 - 780.0]:"
        ctk.CTkLabel(self, text=wl_lbl, font=font_lbl).pack(anchor="e" if is_fa else "w", padx=24, pady=(4, 2))
        self.entry_wl = ctk.CTkEntry(self, font=font_entry)
        self.entry_wl.insert(0, "580.0")
        self.entry_wl.pack(fill="x", padx=24, pady=(0, 8))
        self.entry_wl.bind("<KeyRelease>", self._update_preview)

        # Relative Intensity
        int_lbl = "شدت نسبی [۰.۱ تا ۱.۰]:" if is_fa else "Relative Intensity [0.1 - 1.0]:"
        ctk.CTkLabel(self, text=int_lbl, font=font_lbl).pack(anchor="e" if is_fa else "w", padx=24, pady=(4, 2))
        self.entry_int = ctk.CTkEntry(self, font=font_entry)
        self.entry_int.insert(0, "1.0")
        self.entry_int.pack(fill="x", padx=24, pady=(0, 10))

        # Color Preview Swatch
        self.swatch = ctk.CTkFrame(self, height=22, fg_color="#FFFF00", corner_radius=4)
        self.swatch.pack(fill="x", padx=24, pady=(0, 14))
        self._update_preview()

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkButton(
            btn_frame,
            text="ثبت خط طیفی" if is_fa else "Add Line",
            font=font_btn,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._on_submit
        ).pack(side="right" if is_fa else "left", expand=True, padx=4)

        ctk.CTkButton(
            btn_frame,
            text="انصراف" if is_fa else "Cancel",
            font=font_btn,
            fg_color="#475569",
            hover_color="#334155",
            command=self.destroy
        ).pack(side="left" if is_fa else "right", expand=True, padx=4)

    def _update_preview(self, event=None):
        wl = NumericInput.parse_float(self.entry_wl.get(), default=550.0, min_val=380.0, max_val=780.0)
        hex_col = ColorUtils.wavelength_to_hex(wl)
        self.swatch.configure(fg_color=hex_col)

    def _on_submit(self):
        name = self.entry_name.get().strip() or "Custom Line"
        wl = NumericInput.parse_float(self.entry_wl.get(), default=550.0, min_val=380.0, max_val=780.0)
        intensity = NumericInput.parse_float(self.entry_int.get(), default=1.0, min_val=0.1, max_val=1.0)
        hex_col = ColorUtils.wavelength_to_hex(wl)

        new_line = SpectralLine(
            name=name,
            wavelength_nm=wl,
            intensity=intensity,
            color_hint=hex_col
        )
        self.on_add(new_line)
        self.destroy()
