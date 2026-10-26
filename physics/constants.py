"""
Spectral Line Constants and Grating Specifications for Optical Spectrometry.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from config import RYDBERG_CONSTANT_H

@dataclass
class SpectralLine:
    """Represents a discrete spectral emission line."""
    name: str
    wavelength_nm: float
    intensity: float = 1.0           # Relative intensity [0.0, 1.0]
    color_hint: Optional[str] = None # Optional fallback hex
    transition: Optional[str] = None
    n_upper: Optional[int] = None    # Upper principal quantum number (e.g. for Balmer series)

@dataclass
class SpectralSource:
    """Represents an atomic or molecular light source."""
    id: str
    name_en: str
    name_fa: str
    description_en: str
    description_fa: str
    lines: List[SpectralLine] = field(default_factory=list)
    is_continuous: bool = False
    temperature_k: float = 3200.0


SPECTRAL_SOURCES: Dict[str, SpectralSource] = {
    "Mercury (Hg)": SpectralSource(
        id="Hg",
        name_en="Mercury (Hg)",
        name_fa="بخار جیوه (Hg)",
        description_en="Mercury vapor discharge lamp — standard laboratory wavelength calibration reference.",
        description_fa="لامپ تخلیه بخار جیوه — مرجع استاندارد آزمایشگاهی کالیبراسیون طول‌موج.",
        lines=[
            SpectralLine("Yellow 2", 579.066, intensity=0.75, color_hint="#FFD700", transition="6¹P₁ - 6¹D₂"),
            SpectralLine("Yellow 1", 576.960, intensity=0.80, color_hint="#FFEE00", transition="6¹P₁ - 6³D₂"),
            SpectralLine("Green",    546.074, intensity=1.00, color_hint="#00FF00", transition="6³P₂ - 7³S₁"),
            SpectralLine("Blue-Green", 491.604, intensity=0.18, color_hint="#00E5EE", transition="6³P₀ - 8³S₁"),
            SpectralLine("Blue-Violet", 435.833, intensity=0.90, color_hint="#4B0082", transition="6³P₁ - 7³S₁"),
            SpectralLine("Violet 1", 407.783, intensity=0.30, color_hint="#8A2BE2", transition="6³P₁ - 7¹S₀"),
            SpectralLine("Violet 2", 404.656, intensity=0.65, color_hint="#7B1FA2", transition="6³P₀ - 7³S₁"),
        ]
    ),
    "Sodium (Na)": SpectralSource(
        id="Na",
        name_en="Sodium (Na)",
        name_fa="بخار سدیم (Na)",
        description_en="Low-pressure sodium vapor lamp — iconic yellow doublet (D-lines) for resolving power tests.",
        description_fa="لامپ بخار سدیم کم‌فشار — خطوط دوتایی زرد شاخص (خطوط D) برای آزمون توان تفکیک.",
        lines=[
            SpectralLine("D2", 588.995, intensity=1.00, color_hint="#FFB300", transition="3p ²P₃/₂ → 3s ²S₁/₂"),
            SpectralLine("D1", 589.592, intensity=0.70, color_hint="#FFA000", transition="3p ²P₁/₂ → 3s ²S₁/₂"),
        ]
    ),
    "Hydrogen (H)": SpectralSource(
        id="H",
        name_en="Hydrogen (H)",
        name_fa="اتم هیدروژن (H)",
        description_en="Atomic hydrogen Balmer emission series — used to determine the Rydberg constant R_H.",
        description_fa="سری بالمر طیف گسیلی هیدروژن اتمی — مورد استفاده برای تعیین ثابت ریدبرگ R_H.",
        lines=[
            SpectralLine("H-alpha", 656.280, intensity=1.00, color_hint="#FF2222", transition="n=3 → n=2", n_upper=3),
            SpectralLine("H-beta",  486.133, intensity=0.70, color_hint="#00FFFF", transition="n=4 → n=2", n_upper=4),
            SpectralLine("H-gamma", 434.047, intensity=0.40, color_hint="#4169E1", transition="n=5 → n=2", n_upper=5),
            SpectralLine("H-delta", 410.174, intensity=0.20, color_hint="#8A2BE2", transition="n=6 → n=2", n_upper=6),
        ]
    ),
    "Helium (He)": SpectralSource(
        id="He",
        name_en="Helium (He)",
        name_fa="گاز هلیوم (He)",
        description_en="Helium gas discharge lamp — prominent singlet and triplet emission transitions.",
        description_fa="لامپ تخلیه گاز هلیوم — خطوط گسیلی شاخص سینگلت و تریپلت.",
        lines=[
            SpectralLine("Red",        667.815, intensity=0.60, color_hint="#FF3300", transition="2¹P - 3¹D"),
            SpectralLine("Yellow",     587.562, intensity=1.00, color_hint="#FFD700", transition="2³P - 3³D"),
            SpectralLine("Green",      501.567, intensity=0.50, color_hint="#00FF66", transition="2¹S - 3¹P"),
            SpectralLine("Blue-Green", 492.193, intensity=0.40, color_hint="#00E5EE", transition="2¹P - 4¹D"),
            SpectralLine("Blue",       471.314, intensity=0.35, color_hint="#1E90FF", transition="2³P - 4³S"),
            SpectralLine("Violet",     447.148, intensity=0.80, color_hint="#8A2BE2", transition="2³P - 4³D"),
        ]
    ),
    "Neon (Ne)": SpectralSource(
        id="Ne",
        name_en="Neon (Ne)",
        name_fa="گاز نئون (Ne)",
        description_en="Neon discharge lamp — dense orange and red emission bands.",
        description_fa="لامپ تخلیه گاز نئون — خطوط متراکم نارنجی و قرمز.",
        lines=[
            SpectralLine("Ne 650.6", 650.653, intensity=0.85, color_hint="#FF3300"),
            SpectralLine("Ne 640.2", 640.225, intensity=1.00, color_hint="#FF4500"),
            SpectralLine("Ne 633.4", 633.443, intensity=0.60, color_hint="#FF5722"),
            SpectralLine("Ne 614.3", 614.306, intensity=0.80, color_hint="#FF7043"),
            SpectralLine("Ne 585.2", 585.249, intensity=0.70, color_hint="#FFA726"),
        ]
    ),
    "White Light (Continuous)": SpectralSource(
        id="White",
        name_en="White Light (Continuous)",
        name_fa="نور سفید پیوسته",
        description_en="Tungsten halogen continuous blackbody spectrum spanning 380 to 780 nm.",
        description_fa="چشمه پیوسته جسم سیاه تنگستن هالوژن در گستره ۳۸۰ تا ۷۸۰ نانومتر.",
        lines=[],
        is_continuous=True,
        temperature_k=3200.0
    ),
    "Monochromatic Laser": SpectralSource(
        id="Laser",
        name_en="Monochromatic Laser",
        name_fa="لیزر تک‌فام",
        description_en="Tunable monochromatic laser line for fundamental calibration.",
        description_fa="باریکه لیزر تک‌فام با طول‌موج مشخص جهت کالیبراسیون پایه.",
        lines=[
            SpectralLine("Laser Core", 632.800, intensity=1.00, color_hint="#FF0000", transition="He-Ne Cavity")
        ]
    ),
    "Custom (User Defined)": SpectralSource(
        id="Custom",
        name_en="Custom (User Defined)",
        name_fa="چشمه سفارشی کاربر",
        description_en="User-defined custom spectral emission lines.",
        description_fa="خطوط طیفی سفارشی تعریف‌شده توسط کاربر.",
        lines=[
            SpectralLine("Custom Line 1", 500.000, intensity=1.00, color_hint="#00FFCC"),
            SpectralLine("Custom Line 2", 600.000, intensity=0.80, color_hint="#FF9900"),
        ]
    ),
    "Mystery Element (A)": SpectralSource(
        id="Unknown_A",
        name_en="Mystery Element (A)",
        name_fa="عنصر مجهول (آزمون الف)",
        description_en="Unknown gas discharge lamp — measure lines and deduce identity in Blind Test.",
        description_fa="لامپ تخلیه گاز مجهول — زوایا را بسنجید و عنصر را در چالش تشخیص دهید.",
        lines=[
            SpectralLine("Line 1", 588.995, intensity=1.00),
            SpectralLine("Line 2", 589.592, intensity=0.70),
        ]
    ),
    "Mystery Element (B)": SpectralSource(
        id="Unknown_B",
        name_en="Mystery Element (B)",
        name_fa="عنصر مجهول (آزمون ب)",
        description_en="Unknown gas discharge lamp — measure lines and deduce identity in Blind Test.",
        description_fa="لامپ تخلیه گاز مجهول — زوایا را بسنجید و عنصر را در چالش تشخیص دهید.",
        lines=[
            SpectralLine("Line 1", 579.066, intensity=0.75),
            SpectralLine("Line 2", 576.960, intensity=0.80),
            SpectralLine("Line 3", 546.074, intensity=1.00),
            SpectralLine("Line 4", 435.833, intensity=0.90),
            SpectralLine("Line 5", 404.656, intensity=0.65),
        ]
    )
}

PRISM_PRESETS: Dict[str, Dict[str, Any]] = {
    "Dense Flint Glass (A=60°)": {
        "name_en": "Dense Flint Glass (A=60°)",
        "name_fa": "شیشه فلینت متراکم (A = ۶۰°)",
        "apex_angle_deg": 60.0,
        "cauchy_A": 1.620,
        "cauchy_B_nm2": 12500.0,
        "description_en": "High dispersion flint glass prism (A=1.620, B=12500 nm²).",
        "description_fa": "منشور شیشه فلینت با پاشندگی بالا (A=۱.۶۲۰، B=۱۲۵۰۰ نانومتر مربع)."
    },
    "Crown Glass (A=60°)": {
        "name_en": "Crown Glass (A=60°)",
        "name_fa": "شیشه کراون استاندارد (A = ۶۰°)",
        "apex_angle_deg": 60.0,
        "cauchy_A": 1.510,
        "cauchy_B_nm2": 5400.0,
        "description_en": "Standard optical crown glass prism (A=1.510, B=5400 nm²).",
        "description_fa": "منشور شیشه کراون اپتیکی استاندارد (A=۱.۵۱۰، B=۵۴۰۰ نانومتر مربع)."
    }
}

GRATING_PRESETS: Dict[str, Dict[str, Any]] = {
    "100 lines/mm": {
        "n_lines_per_mm": 100.0,
        "d_nm": 10000.0,
        "description_en": "Coarse grating (d = 10.0 µm) — low dispersion, high orders.",
        "description_fa": "توری درشت (d = ۱۰.۰ میکرومتر) — پاشندگی کم، مرتبه‌های بالا."
    },
    "300 lines/mm": {
        "n_lines_per_mm": 300.0,
        "d_nm": 3333.333,
        "description_en": "Standard introductory grating (d = 3.33 µm).",
        "description_fa": "توری استاندارد آموزشی مقدماتی (d = ۳.۳۳ میکرومتر)."
    },
    "600 lines/mm": {
        "n_lines_per_mm": 600.0,
        "d_nm": 1666.667,
        "description_en": "Classic laboratory grating (d = 1.67 µm) — resolves sodium D-lines in 1st order.",
        "description_fa": "توری کلاسیک آزمایشگاهی (d = ۱.۶۷ میکرومتر) — تفکیک خطوط سدیم در مرتبه اول."
    },
    "1200 lines/mm": {
        "n_lines_per_mm": 1200.0,
        "d_nm": 833.333,
        "description_en": "High-resolution grating (d = 0.83 µm) — large angular dispersion.",
        "description_fa": "توری با قدرت تفکیک بالا (d = ۰.۸۳ میکرومتر) — پاشندگی زاویه‌ای زیاد."
    }
}
