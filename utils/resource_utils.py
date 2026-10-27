"""
Resource and asset path management for development and PyInstaller bundled builds.
Provides safe multi-size window icon application for Tk and CustomTkinter windows.
"""

import os
import sys
import tkinter as tk
from typing import Optional
from PIL import Image, ImageTk

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller _MEIPASS.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # Project root directory: D:\SpectroMeter Simulator
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_path, relative_path))

def apply_window_icon(window: tk.Wm):
    """
    Applies multi-size .ico and PhotoImage fallback to any Tk or CTkToplevel window.
    Ensures crisp rendering on Windows taskbar and window title bar.
    """
    ico_path = resource_path(os.path.join("assets", "Logo", "favicon.ico"))
    png_path = resource_path(os.path.join("assets", "Logo", "icon.png"))

    if os.path.exists(ico_path):
        try:
            window.iconbitmap(ico_path)
        except Exception:
            pass

    if os.path.exists(png_path):
        try:
            pil_img = Image.open(png_path).resize((64, 64), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            window.iconphoto(False, photo)
            # Retain reference to prevent garbage collection
            window._app_icon_ref = photo
        except Exception:
            pass
