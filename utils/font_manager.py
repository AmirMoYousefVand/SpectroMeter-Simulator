"""
Centralized Font Management Service.
Dynamically registers Vazirmatn (Persian typography) and Space Grotesk (Latin/Numerics)
into Windows GDI and Matplotlib font caches without requiring system installation.
"""

import sys
import os
import ctypes
from typing import Optional
import customtkinter as ctk
import matplotlib.font_manager as fm

class FontManager:
    """Manages cross-platform font loading and provides CTkFont and Matplotlib font instances."""

    _INITIALIZED = False
    _FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")

    PERSIAN_FAMILY = "Vazirmatn"
    ENGLISH_FAMILY = "Space Grotesk"
    MONO_FAMILY = "Consolas"

    @classmethod
    def initialize(cls):
        """Loads font files into Windows GDI and Matplotlib fontManager."""
        if cls._INITIALIZED:
            return

        font_files = [
            os.path.join(cls._FONT_DIR, "Vazirmatn-Regular.ttf"),
            os.path.join(cls._FONT_DIR, "Vazirmatn-Bold.ttf"),
            os.path.join(cls._FONT_DIR, "SpaceGrotesk.ttf")
        ]

        is_win = sys.platform.startswith("win")

        for fpath in font_files:
            if os.path.exists(fpath):
                abs_path = os.path.abspath(fpath)
                # 1. Register with Windows GDI (FR_PRIVATE = 0x10)
                if is_win:
                    try:
                        ctypes.windll.gdi32.AddFontResourceExW(abs_path, 0x10, 0)
                    except Exception as e:
                        print(f"Warning: GDI font load failed for {fpath}: {e}")

                # 2. Register with Matplotlib
                try:
                    fm.fontManager.addfont(abs_path)
                except Exception as e:
                    print(f"Warning: Matplotlib addfont failed for {fpath}: {e}")

        cls._INITIALIZED = True

    @classmethod
    def get_persian_font(cls, size: int = 12, weight: str = "normal") -> ctk.CTkFont:
        """Returns Vazirmatn font instance for Persian text."""
        cls.initialize()
        return ctk.CTkFont(family=cls.PERSIAN_FAMILY, size=size, weight=weight)

    @classmethod
    def get_number_font(cls, size: int = 12, weight: str = "bold") -> ctk.CTkFont:
        """Returns Space Grotesk font instance for numerical metrics and English labels."""
        cls.initialize()
        return ctk.CTkFont(family=cls.ENGLISH_FAMILY, size=size, weight=weight)

    @classmethod
    def get_ui_font(cls, size: int = 12, weight: str = "normal", is_persian: bool = True) -> ctk.CTkFont:
        """Returns appropriate font based on language flag."""
        cls.initialize()
        fam = cls.PERSIAN_FAMILY if is_persian else cls.ENGLISH_FAMILY
        return ctk.CTkFont(family=fam, size=size, weight=weight)

    @classmethod
    def get_mpl_persian_prop(cls, size: int = 9) -> fm.FontProperties:
        """Returns Matplotlib FontProperties configured for Persian text."""
        cls.initialize()
        return fm.FontProperties(family=[cls.PERSIAN_FAMILY, "Tahoma", "DejaVu Sans", "sans-serif"], size=size)

    @classmethod
    def get_mpl_number_prop(cls, size: int = 9) -> fm.FontProperties:
        """Returns Matplotlib FontProperties configured for Latin/Numbers."""
        cls.initialize()
        return fm.FontProperties(family=[cls.ENGLISH_FAMILY, "DejaVu Sans", "sans-serif"], size=size)
