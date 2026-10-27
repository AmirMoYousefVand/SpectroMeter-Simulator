"""
Unknown Element Blind Spectroscopy Quiz Dialog (آزمون تعاملی تشخیص عنصر مجهول).
Enables students to test their analytical skills: observe unlabelled emission lines,
calculate experimental wavelengths, and submit their deduction for scoring.
"""

from typing import Callable, Optional
import customtkinter as ctk

from physics.constants import SPECTRAL_SOURCES
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.numeric_input import NumericInput
from utils.resource_utils import apply_window_icon

class UnknownElementDialog(ctk.CTkToplevel):
    """Interactive quiz window for identifying unknown gas discharge lamps."""

    def __init__(self, master, current_source_key: str, **kwargs):
        super().__init__(master, **kwargs)
        self.current_source_key = current_source_key

        is_fa = LocalizationService.is_persian()
        self.title("چالش تشخیص عنصر مجهول" if is_fa else "Unknown Element Identification Quiz")
        self.geometry("450x420")
        self.resizable(False, False)
        self.grab_set()

        apply_window_icon(self)
        self._create_widgets()

    def _create_widgets(self):
        is_fa = LocalizationService.is_persian()
        font_h = FontManager.get_ui_font(14, "bold", is_fa)
        font_lbl = FontManager.get_ui_font(12, "bold", is_fa)
        font_body = FontManager.get_ui_font(11, "normal", is_fa)
        font_num = FontManager.get_number_font(11, "bold")
        font_btn = FontManager.get_ui_font(12, "bold", is_fa)

        self.grid_columnconfigure(0, weight=1)

        # Header
        t_text = "آزمون کلاسی: هویت این گاز گسیلی چیست؟" if is_fa else "Classroom Quiz: Identify the Unknown Gas"
        ctk.CTkLabel(self, text=t_text, font=font_h, text_color="#38BDF8").pack(pady=(16, 6))

        intro_text = (
            "با چرخاندن تلسکوپ و خواندن دقیق زوایا از روی ورنیه، طول‌موج خطوط را محاسبه کنید.\nسپس حدس خود از هویت عنصر را انتخاب کنید:"
        ) if is_fa else (
            "Measure the angles using the dual Verniers, compute wavelengths, and submit your deduction:"
        )
        ctk.CTkLabel(self, text=intro_text, font=font_body, text_color="#E2E8F0", justify="center").pack(pady=(0, 12), padx=20)

        # Element Guess Dropdown
        cand_lbl = "حدس شما از هویت عنصر:" if is_fa else "Your deduction of the gas:"
        ctk.CTkLabel(self, text=cand_lbl, font=font_lbl).pack(anchor="e" if is_fa else "w", padx=30, pady=(2, 2))

        candidate_options = [
            "Sodium (Na) - بخار سدیم",
            "Mercury (Hg) - بخار جیوه",
            "Hydrogen (H) - گاز هیدروژن",
            "Helium (He) - گاز هلیوم",
            "Neon (Ne) - گاز نئون"
        ]
        self.guess_menu = ctk.CTkOptionMenu(
            self,
            values=candidate_options,
            font=FontManager.get_persian_font(11, "bold") if is_fa else font_num,
            dropdown_font=FontManager.get_persian_font(11) if is_fa else font_num
        )
        self.guess_menu.pack(fill="x", padx=30, pady=(0, 10))

        # Wavelength inputs
        wl1_lbl = "طول‌موج برجسته‌ترین خط مشاهده‌شده (nm):" if is_fa else "Prominent line wavelength (nm):"
        ctk.CTkLabel(self, text=wl1_lbl, font=font_lbl).pack(anchor="e" if is_fa else "w", padx=30, pady=(2, 2))
        self.entry_wl = ctk.CTkEntry(self, font=font_num, placeholder_text="e.g. 589.0 or 546.1")
        self.entry_wl.pack(fill="x", padx=30, pady=(0, 14))

        # Feedback Result Label
        self.feedback_lbl = ctk.CTkLabel(self, text="", font=font_lbl, wraplength=400)
        self.feedback_lbl.pack(pady=4)

        # Submit / Cancel Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(6, 16))

        ctk.CTkButton(
            btn_row,
            text="بررسی پاسخ" if is_fa else "Verify Deduction",
            font=font_btn,
            fg_color="#059669",
            hover_color="#047857",
            command=self._verify_deduction
        ).pack(side="right" if is_fa else "left", expand=True, padx=4)

        ctk.CTkButton(
            btn_row,
            text="بستن" if is_fa else "Close",
            font=font_btn,
            fg_color="#475569",
            hover_color="#334155",
            command=self.destroy
        ).pack(side="left" if is_fa else "right", expand=True, padx=4)

    def _verify_deduction(self):
        is_fa = LocalizationService.is_persian()
        guess = self.guess_menu.get()

        # True identity from current_source_key
        # Mystery A = Sodium, Mystery B = Mercury
        is_correct = False
        true_name = ""

        if "Mystery Element (A)" in self.current_source_key:
            true_name = "Sodium (Na)"
            is_correct = "Sodium" in guess or "سدیم" in guess
        elif "Mystery Element (B)" in self.current_source_key:
            true_name = "Mercury (Hg)"
            is_correct = "Mercury" in guess or "جیوه" in guess
        else:
            # Active source is already known
            true_name = self.current_source_key
            is_correct = true_name[:4] in guess

        if is_correct:
            msg = f"✓ آفرین! پاسخ کاملاً درست است. عنصر مجهول {true_name} بود." if is_fa else f"✓ Correct! The unknown gas was indeed {true_name}."
            self.feedback_lbl.configure(text=msg, text_color="#10B981")
        else:
            msg = f"✗ درست نبود. دوباره اندازه‌گیری کنید یا خطوط دیگر را بسنجید." if is_fa else "✗ Incorrect deduction. Inspect other spectral lines or re-measure angles."
            self.feedback_lbl.configure(text=msg, text_color="#EF4444")
