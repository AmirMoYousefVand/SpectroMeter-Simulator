"""
Localization Service providing bilingual (English & Persian) labels,
physical terminology, tooltips, presets, and educational descriptions.
Maintains clean standard Unicode for CustomTkinter widgets and provides
dedicated text reshaping for Matplotlib and Tkinter Canvas.
"""

from typing import Dict, Any, Optional
import functools
import re
import arabic_reshaper
from bidi.algorithm import get_display

# Unicode Right-to-Left Mark (kept for backward compatibility where needed)
RLM = "‏"

class LocalizationService:
    """Manages bilingual UI strings (English & Persian) with clean RTL formatting."""

    _CURRENT_LANG = "fa"  # Default to Persian

    STRINGS: Dict[str, Dict[str, str]] = {
        # App Title & Headers
        "app_title": {
            "en": "Optical Spectrometer & Diffraction Grating Simulator",
            "fa": "شبیه‌ساز دقیق اسپکترومتر اپتیکی و توری پراش"
        },
        "app_subtitle": {
            "en": "Precision Goniometric Spectroscopy & Spectral Line Analysis Lab",
            "fa": "آزمایشگاه گونیومتری پیشرفته و تحلیل خطوط طیفی اتمی"
        },
        "lang_switch": {
            "en": "فارسی (FA)",
            "fa": "English (EN)"
        },
        "theme_toggle": {
            "en": "Theme",
            "fa": "پوسته"
        },
        "audio_toggle": {
            "en": "Sound",
            "fa": "صدا"
        },

        # Tabs
        "tab_eyepiece": {
            "en": "1. Eyepiece & Reticle",
            "fa": "۱. چشمی و رتیکول"
        },
        "tab_verniers": {
            "en": "2. Dual Verniers Zoom",
            "fa": "۲. ذره‌بین ورنیه‌ها"
        },
        "tab_app_2d": {
            "en": "3. 2D Setup & Rays",
            "fa": "۳. نمای بالای دستگاه"
        },
        "tab_app_3d": {
            "en": "4. 3D Apparatus",
            "fa": "۴. نمای سه‌بعدی"
        },
        "tab_profile_1d": {
            "en": "5. Spectral Profile",
            "fa": "۵. پروفایل شدت طیف"
        },
        "tab_calc": {
            "en": "6. Equations & Worksheets",
            "fa": "۶. محاسبات و گزارش"
        },
        "tab_guide": {
            "en": "7. Lab Guide & Theory",
            "fa": "۷. راهنما و روش شوستر"
        },

        # Control Panel Titles
        "panel_sources": {
            "en": "Light Source & Grating",
            "fa": "چشمه نور و توری پراش"
        },
        "panel_mechanics": {
            "en": "Telescope & Gonio Controls",
            "fa": "کنترل تلسکوپ و گونیومتر"
        },
        "panel_optics": {
            "en": "Optics & Alignment Knobs",
            "fa": "تنظیمات اپتیک و فوکوس"
        },
        "panel_errors": {
            "en": "Real Systematic Errors",
            "fa": "شبیه‌سازی خطاهای واقعی"
        },

        # Controls & Sliders
        "lbl_lamp": {
            "en": "Spectral Source:",
            "fa": "چشمه گسیلی:"
        },
        "lbl_custom_btn": {
            "en": "+ Custom Line",
            "fa": "+ خط سفارشی"
        },
        "lbl_grating": {
            "en": "Diffraction Grating:",
            "fa": "توری پراش:"
        },
        "lbl_d_constant": {
            "en": "Grating Constant (d):",
            "fa": "ثابت توری (d):"
        },
        "lbl_slit_width": {
            "en": "Entrance Slit Width:",
            "fa": "پهنای شکاف ورودی:"
        },
        "lbl_tele_focus": {
            "en": "Telescope Objective Focus:",
            "fa": "فوکوس شیئی تلسکوپ:"
        },
        "lbl_coll_focus": {
            "en": "Collimator Focus:",
            "fa": "فوکوس موازی‌ساز:"
        },
        "lbl_reticle_light": {
            "en": "Reticle Illumination:",
            "fa": "روشنایی رتیکول:"
        },

        # Telescope Mechanics
        "lbl_clamp": {
            "en": "Arm Clamp Screw:",
            "fa": "پیچ قفل بازو:"
        },
        "btn_clamp_locked": {
            "en": "LOCKED (Fine Active)",
            "fa": "قفل (پیچ ظریف فعال)"
        },
        "btn_clamp_free": {
            "en": "FREE (Coarse Active)",
            "fa": "آزاد (چرخش سریع فعال)"
        },
        "lbl_coarse_angle": {
            "en": "Telescope Angle (Coarse):",
            "fa": "زاویه تلسکوپ (چرخش کلی):"
        },
        "lbl_fine_tangent": {
            "en": "Fine Tangent Micrometer:",
            "fa": "پیچ حرکت ظریف میکرومتری:"
        },
        "btn_center_zero": {
            "en": "Align 0° (Central)",
            "fa": "تراز روی ۰° (مرکزی)"
        },
        "btn_add_measurement": {
            "en": "Record Current Angle",
            "fa": "ثبت در جدول آزمایش"
        },

        # Errors
        "sw_enable_errors": {
            "en": "Simulate Systematic Errors",
            "fa": "فعال‌سازی خطاهای واقعی"
        },
        "sw_digital_helper": {
            "en": "Digital Angle Helper",
            "fa": "نمایشگر دیجیتال کمکی"
        },
        "lbl_table_tilt": {
            "en": "Grating Table Leveling Tilt:",
            "fa": "تراز میز توری (روش شوستر):"
        },
        "lbl_eccentricity": {
            "en": "Vernier Axis Eccentricity:",
            "fa": "خروج از مرکز محور ورنیه:"
        },
        "lbl_oblique": {
            "en": "Oblique Incidence Angle:",
            "fa": "زاویه فرود مایل:"
        },

        # Telemetry Bar
        "tel_tele_angle": {
            "en": "Telescope θ",
            "fa": "زاویه تلسکوپ θ"
        },
        "tel_vernier_1": {
            "en": "Vernier 1 (V₁)",
            "fa": "ورنیه ۱ (V₁)"
        },
        "tel_vernier_2": {
            "en": "Vernier 2 (V₂)",
            "fa": "ورنیه ۲ (V₂)"
        },
        "tel_active_line": {
            "en": "Observed Line",
            "fa": "خط در مرکز رتیکول"
        },
        "tel_order": {
            "en": "Order (m):",
            "fa": "مرتبه (m):"
        },
        "tel_resolving_power": {
            "en": "Resolving Power (R):",
            "fa": "توان تفکیک (R):"
        },
        "none_detected": {
            "en": "Dark Field",
            "fa": "میدان تاریک"
        },

        # Exports & Reports
        "btn_export_word": {
            "en": "Export Word (.docx) Report",
            "fa": "صدور گزارش کار Word (.docx)"
        },
        "btn_export_csv": {
            "en": "Export CSV Data",
            "fa": "ذخیره داده‌های CSV"
        },
        "btn_export_plot": {
            "en": "Save High-Res Plot (PNG)",
            "fa": "ذخیره نمودار با کیفیت بالا"
        },
        "btn_clear_table": {
            "en": "Clear Table",
            "fa": "پاک کردن جدول"
        },
        "btn_reset_params": {
            "en": "Reset All Parameters",
            "fa": "بازنشانی پارامترها"
        },
        "optic_mode_label": {
            "en": "Dispersive Optic Element:",
            "fa": "قطعه پاشنده نوری:"
        },
        "optic_grating": {
            "en": "Diffraction Grating",
            "fa": "توری پراش"
        },
        "optic_prism": {
            "en": "Equilateral Prism (A=60°)",
            "fa": "منشور شیشه‌ای (۶۰°)"
        },
        "darkroom_toggle": {
            "en": "Darkroom",
            "fa": "تاریکخانه"
        },
        "btn_blind_quiz": {
            "en": "Blind Element Quiz",
            "fa": "چالش عنصر مجهول"
        },

        # Vernier View Texts
        "vernier_1_title": {
            "en": "VERNIER 1 (V₁ — Main Axis)",
            "fa": "ورنیه ۱ (V₁ — محور اصلی)"
        },
        "vernier_2_title": {
            "en": "VERNIER 2 (V₂ — 180° Opposite)",
            "fa": "ورنیه ۲ (V₂ — ۱۸۰ درجه مقابل)"
        },
        "eccentricity_active": {
            "en": "Eccentricity Compensation: Active (V₁ & V₂ averaged)",
            "fa": "جبران خطای خروج از مرکز: فعال (میانگین V₁ و V₂)"
        },

        # 3D View Toolbar Texts
        "cam_label": {
            "en": "Camera:",
            "fa": "دوربین:"
        },
        "cam_perspective": {
            "en": "Perspective",
            "fa": "پرسپکتیو"
        },
        "cam_top": {
            "en": "Top (2D)",
            "fa": "از بالا"
        },
        "cam_eyepiece": {
            "en": "Eyepiece",
            "fa": "هم‌تراز چشمی"
        },
        "cam_front": {
            "en": "Front",
            "fa": "روبرو"
        },
        "rot_label": {
            "en": "Rotate:",
            "fa": "چرخش:"
        },
    }

    @classmethod
    def get_language(cls) -> str:
        return cls._CURRENT_LANG

    @classmethod
    def set_language(cls, lang: str):
        if lang in ("fa", "en"):
            cls._CURRENT_LANG = lang

    @classmethod
    def toggle_language(cls) -> str:
        cls._CURRENT_LANG = "en" if cls._CURRENT_LANG == "fa" else "fa"
        return cls._CURRENT_LANG

    @classmethod
    def is_persian(cls) -> bool:
        return cls._CURRENT_LANG == "fa"

    @classmethod
    def t(cls, key: str) -> str:
        """
        Returns clean localized string for CustomTkinter widgets.
        Does NOT apply BiDi reversal so Windows Uniscribe shapes text properly.
        """
        entry = cls.STRINGS.get(key)
        if not entry:
            return key
        return entry.get(cls._CURRENT_LANG, entry.get("en", key))

    @classmethod
    @functools.lru_cache(maxsize=1024)
    def reshape_text(cls, text: str) -> str:
        """
        Transforms Persian/Arabic text for Matplotlib and graphic renderers
        lacking native complex text layout (Uniscribe/HarfBuzz).
        """
        if not text:
            return ""

        # Remove invisible directional control codes
        clean = re.sub(r"[‎‏‪-‮⁦-⁩]", "", str(text))

        # Check if text contains Arabic/Persian range
        has_persian = any(
            '؀' <= ch <= 'ۿ' or
            'ݐ' <= ch <= 'ݿ' or
            'ﭐ' <= ch <= '﷿' or
            'ﹰ' <= ch <= '﻿'
            for ch in clean
        )
        if not has_persian:
            return clean

        reshaped = arabic_reshaper.reshape(clean)
        return get_display(reshaped)

    @classmethod
    def render_canvas_persian(
        cls,
        canvas: Any,
        x: float,
        y: float,
        text: str,
        font: Any = ("Vazirmatn", 10),
        fill: str = "#FFFFFF",
        anchor: str = "center",
        **kwargs
    ) -> int:
        """
        Renders clean Persian text on Tkinter Canvas.
        """
        if not text:
            return -1
        clean = re.sub(r"[‎‏‪-‮⁦-⁩]", "", str(text))
        has_persian = any(
            '؀' <= ch <= 'ۿ' or
            'ݐ' <= ch <= 'ݿ' or
            'ﭐ' <= ch <= '﷿' or
            'ﹰ' <= ch <= '﻿'
            for ch in clean
        )
        if cls.is_persian() and has_persian:
            reshaped = arabic_reshaper.reshape(clean)
            final_text = get_display(reshaped)
        else:
            final_text = clean
        return canvas.create_text(x, y, text=final_text, font=font, fill=fill, anchor=anchor, **kwargs)
