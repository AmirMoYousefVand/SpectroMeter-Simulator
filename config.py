"""
Configuration and Physical Constants for Optical Spectrometer Simulator.
"""

from typing import Dict, Any

# ==============================================================================
# Application Metadata & Window Defaults
# ==============================================================================
APP_TITLE = "Optical Spectrometer & Diffraction Grating Simulator"
APP_SUBTITLE = "High-Precision Goniometric Spectroscopy Lab"
APP_VERSION = "1.0.0"

APPEARANCE_MODE = "Dark"
COLOR_THEME = "blue"

WINDOW_DEFAULT_GEOMETRY = "1420x920"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
ANIMATION_INTERVAL_MS = 16  # ~60 FPS

# ==============================================================================
# Fundamental Physical Constants (CODATA Standard)
# ==============================================================================
SPEED_OF_LIGHT = 299792458.0              # m/s (c)
PLANCK_CONSTANT = 6.62607015e-34          # J*s (h)
ELEMENTARY_CHARGE = 1.602176634e-19       # C (e)
RYDBERG_CONSTANT_H = 1.0973731568160e7    # m^-1 (R_H for Hydrogen)

# ==============================================================================
# Vernier & Scale Mechanics
# ==============================================================================
MAIN_SCALE_DIV_DEG = 0.5                  # 30 arcminutes per main division
VERNIER_DIVISIONS = 30                    # 30 subdivisions
LEAST_COUNT_ARCMIN = 1.0                  # 1 arcminute (1')
LEAST_COUNT_DEG = 1.0 / 60.0              # 1/60 degrees

# ==============================================================================
# Optical Defaults
# ==============================================================================
DEFAULT_LAMP = "Mercury (Hg)"
DEFAULT_GRATING = "600 lines/mm"
DEFAULT_SLIT_WIDTH_MM = 0.05              # 50 micrometers
DEFAULT_TELESCOPE_FOCUS = 50.0            # 50% = in-focus
DEFAULT_COLLIMATOR_FOCUS = 50.0           # 50% = in-focus
DEFAULT_RETICLE_ILLUMINATION = 80.0       # 80%

DEFAULT_BEAM_WIDTH_MM = 15.0              # 15 mm aperture beam width
COLLIMATOR_FOCAL_LENGTH_MM = 178.0        # standard laboratory f_coll
TELESCOPE_FOCAL_LENGTH_MM = 178.0         # standard laboratory f_tele
TELESCOPE_FOV_DEG = 3.0                   # Field of view inside eyepiece: 3 degrees

# Slider Ranges & Parameter Limits
PARAM_LIMITS: Dict[str, Dict[str, Any]] = {
    "telescope_angle_deg": {"min": 0.0, "max": 360.0, "step": 0.01, "default": 0.0},
    "fine_tangent_deg": {"min": -5.0, "max": 5.0, "step": 0.008333, "default": 0.0},
    "slit_width_mm": {"min": 0.01, "max": 0.80, "step": 0.005, "default": 0.05},
    "telescope_focus": {"min": 0.0, "max": 100.0, "step": 1.0, "default": 50.0},
    "collimator_focus": {"min": 0.0, "max": 100.0, "step": 1.0, "default": 50.0},
    "reticle_brightness": {"min": 0.0, "max": 100.0, "step": 5.0, "default": 80.0},
    "grating_lines_per_mm": {"min": 50.0, "max": 2400.0, "step": 10.0, "default": 600.0},
    "table_tilt_x_deg": {"min": -1.0, "max": 1.0, "step": 0.05, "default": 0.0},
    "table_tilt_y_deg": {"min": -1.0, "max": 1.0, "step": 0.05, "default": 0.0},
    "oblique_incidence_deg": {"min": -5.0, "max": 5.0, "step": 0.1, "default": 0.0},
    "eccentricity_um": {"min": 0.0, "max": 50.0, "step": 1.0, "default": 15.0},
}

PARAM_DECIMALS: Dict[str, int] = {
    "telescope_angle_deg": 3,
    "fine_tangent_deg": 4,
    "slit_width_mm": 3,
    "telescope_focus": 1,
    "collimator_focus": 1,
    "reticle_brightness": 0,
    "grating_lines_per_mm": 1,
    "table_tilt_x_deg": 2,
    "table_tilt_y_deg": 2,
    "oblique_incidence_deg": 2,
    "eccentricity_um": 1,
}
