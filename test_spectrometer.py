"""
Comprehensive Test and Verification Suite for Optical Spectrometer Simulator.
Covers:
1. Fraunhofer diffraction angles and grating equation
2. Sodium doublet resolving power and angular dispersion
3. Hydrogen Balmer series and Rydberg constant determination
4. Vernier decomposition, least-count 1', and eccentricity cancellation
5. Hardware kinematics (clamp, fine tangent screw)
6. Systematic error models (defocus PSF, Schuster leveling tilt)
7. Multi-format exports (Word .docx with OMML, CSV with UTF-8 BOM)
8. FontManager and Persian BiDi text reshaping
9. Headless GUI initialization smoke test
"""

import os
import sys
import math
import tempfile
import numpy as np

# Reconfigure stdout to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from physics.constants import SPECTRAL_SOURCES, GRATING_PRESETS, RYDBERG_CONSTANT_H
from physics.spectrometer_model import SpectrometerModel, VernierReading
from physics.grating_engine import GratingEngine, DiffractedPeak
from physics.error_model import SpectrometerErrorModel, ErrorParameters
from utils.color_utils import ColorUtils
from utils.numeric_input import NumericInput
from utils.font_manager import FontManager
from utils.localization import LocalizationService
from utils.audio_effects import AudioEffects
from utils.docx_exporter import DocxEquationExporter
from utils.export_service import ExportService


def test_grating_diffraction_angles():
    print("[1/9] Testing Fraunhofer Grating Diffraction Angles...")
    engine = GratingEngine(lines_per_mm=600.0, slit_width_mm=0.05)

    # For Hg Green (546.074 nm), m = 1
    # sin θ = 600e3 * 546.074e-9 = 0.3276444 => θ ≈ 19.124° (19° 07')
    theta_1 = engine.calculate_diffraction_angle_deg(546.074, order_m=1)
    assert theta_1 is not None, "Diffraction angle should be valid"
    assert abs(theta_1 - 19.124) < 0.05, f"Expected ~19.124°, got {theta_1:.4f}°"

    # Order m = -1 (left side)
    theta_neg1 = engine.calculate_diffraction_angle_deg(546.074, order_m=-1)
    assert theta_neg1 is not None
    assert abs(theta_neg1 - (-19.124)) < 0.05, f"Expected -19.124°, got {theta_neg1:.4f}°"

    # Order m = 0 (central)
    theta_0 = engine.calculate_diffraction_angle_deg(546.074, order_m=0)
    assert abs(theta_0 - 0.0) < 1e-6

    # Order m = 4 should exceed 90° for 600 lines/mm (sin > 1)
    theta_4 = engine.calculate_diffraction_angle_deg(546.074, order_m=4)
    assert theta_4 is None, "Order 4 should be evanescent"
    print("  ✓ Grating diffraction angles verified successfully.")


def test_sodium_doublet_and_resolving_power():
    print("[2/9] Testing Sodium Doublet Resolution & Rayleigh Criterion...")
    engine = GratingEngine(lines_per_mm=600.0, slit_width_mm=0.05, beam_width_mm=15.0)

    # Sodium D1 = 589.592 nm, D2 = 588.995 nm (Δλ ≈ 0.6 nm)
    th_d2 = engine.calculate_diffraction_angle_deg(588.995, order_m=1)
    th_d1 = engine.calculate_diffraction_angle_deg(589.592, order_m=1)

    delta_theta = abs(th_d1 - th_d2)
    assert delta_theta > 0.02, f"Doublet angular separation too small: {delta_theta}°"

    # Resolving power in order m = 1
    # N_t = 15mm / (1/600 mm) = 9000 lines
    assert abs(engine.illuminated_lines_Nt - 9000.0) < 1.0
    r_power = 1 * engine.illuminated_lines_Nt
    min_dlambda = 589.0 / r_power
    # For N_t=9000, min_dlambda = 589 / 9000 ≈ 0.065 nm < 0.6 nm => Well resolved!
    assert min_dlambda < 0.6, f"Should resolve sodium doublet: min Δλ = {min_dlambda:.4f} nm"
    print("  ✓ Sodium doublet and resolving power verified.")


def test_hydrogen_balmer_and_rydberg():
    print("[3/9] Testing Hydrogen Balmer Series & Rydberg Constant Extraction...")
    engine = GratingEngine(lines_per_mm=600.0)

    # H-alpha (656.28 nm, n=3): sin θ = 600e3 * 656.28e-9 = 0.393768 => θ ≈ 23.189°
    th_alpha = engine.calculate_diffraction_angle_deg(656.280, order_m=1)
    res_h = engine.calculate_rydberg_constant(th_alpha, order_m=1, d_m=engine.d_m, n_upper=3)

    r_exp = res_h["R_H_exp"]
    err = res_h["rel_error_percent"]
    assert err < 0.1, f"Rydberg relative error too high: {err:.3f}%"
    assert abs(r_exp - RYDBERG_CONSTANT_H) / RYDBERG_CONSTANT_H < 1e-3
    print(f"  ✓ Calculated R_H: {r_exp:.6e} m⁻¹ (Error: {err:.4f}%).")


def test_vernier_decomposition_and_precision():
    print("[4/9] Testing Vernier Scale Decomposition (Least Count = 1')...")
    # Angle 21.7333° = 21° 44' (MSR = 21° 30', VSR = 14')
    decomp = SpectrometerModel.decompose_angle_to_vernier(21.733333)
    assert decomp.degrees == 21, f"Expected 21°, got {decomp.degrees}"
    assert decomp.msr_arcmin == 30, f"Expected MSR 30', got {decomp.msr_arcmin}'"
    assert decomp.vsr_coincident == 14, f"Expected VSR 14', got {decomp.vsr_coincident}'"
    assert decomp.readout_str == "21° 44'"

    # Angle 0.0°
    d0 = SpectrometerModel.decompose_angle_to_vernier(0.0)
    assert d0.readout_str == "0° 00'"

    # Angle 359.5° = 359° 30'
    d_half = SpectrometerModel.decompose_angle_to_vernier(359.5)
    assert d_half.degrees == 359
    assert d_half.msr_arcmin == 30
    assert d_half.vsr_coincident == 0
    print("  ✓ Vernier decomposition and least-count precision verified.")


def test_kinematics_and_eccentricity_cancellation():
    print("[5/9] Testing Hardware Kinematics & Dual Vernier Eccentricity Cancellation...")
    model = SpectrometerModel()

    # Unclamped coarse rotation
    model.set_coarse_angle(45.5)
    assert abs(model.effective_telescope_angle - 45.5) < 1e-4

    # Clamp lock
    model.toggle_clamp()
    assert model.is_clamped is True

    # Fine tangent screw
    model.set_fine_tangent(0.25) # +15 arcminutes
    assert abs(model.effective_telescope_angle - 45.75) < 1e-4

    # Dual Vernier eccentricity test
    model.enable_eccentricity = True
    model.eccentricity_um = 20.0
    v1, v2 = model.get_vernier_readings()

    # V1 and V2 individually have eccentricity error
    # But their average must accurately recover the true angle!
    corrected_ang = model.get_corrected_angle_from_verniers(v1, v2)
    assert abs(corrected_ang - 45.75) < 0.02, f"Eccentricity cancellation failed: {corrected_ang} vs 45.75"
    print("  ✓ Kinematics and dual vernier eccentricity cancellation verified.")


def test_error_models():
    print("[6/9] Testing Physical Error Models (Defocus PSF & Table Tilt)...")
    err = SpectrometerErrorModel()

    # Default 50% = in-focus => factor = 1.0
    assert abs(err.get_focus_blur_factor() - 1.0) < 1e-4

    # Severe defocus at 0%
    err.params.telescope_focus_percent = 0.0
    err.params.collimator_focus_percent = 0.0
    blur = err.get_focus_blur_factor()
    assert blur > 4.0, f"Defocus blur factor should be high: {blur}"

    # Grating table leveling tilt
    err.params.table_tilt_x_deg = 0.5
    drift, slant = err.get_grating_tilt_offsets(90.0)
    assert abs(drift) > 0.0, "Tilt should induce vertical drift"
    print("  ✓ Physical error models verified.")


def test_exports_docx_and_csv():
    print("[7/9] Testing Word (.docx with OMML) and CSV Exports...")
    model = SpectrometerModel()
    engine = GratingEngine(lines_per_mm=600.0)
    source = SPECTRAL_SOURCES["Mercury (Hg)"]

    dummy_measurements = [
        {
            "index": 1,
            "line_name": "Green",
            "order_m": 1,
            "v1_str": "19° 07'",
            "v2_str": "199° 08'",
            "corr_deg": 19.125,
            "dev_deg": 19.125,
            "true_wl_nm": 546.074,
            "calc_wl_nm": 546.10,
            "error_percent": 0.005
        }
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Test CSV export with BOM
        csv_path = os.path.join(tmp_dir, "test_report.csv")
        ExportService.export_csv(csv_path, dummy_measurements)
        assert os.path.exists(csv_path)
        with open(csv_path, "rb") as f:
            header_bytes = f.read(3)
            assert header_bytes == b'\xef\xbb\xbf', "CSV must contain UTF-8 BOM"

        # Test Word export with OMML
        docx_path = os.path.join(tmp_dir, "test_report.docx")
        DocxEquationExporter.export_report(
            filepath=docx_path,
            model=model,
            grating_engine=engine,
            source=source,
            measurements=dummy_measurements,
            is_persian=True
        )
        assert os.path.exists(docx_path)
        assert os.path.getsize(docx_path) > 5000, "DOCX file too small"
    print("  ✓ Word OMML and CSV exports verified.")


def test_localization_and_fonts():
    print("[8/9] Testing Localization Service & FontManager...")
    FontManager.initialize()

    # Persian shaping without throwing exceptions
    fa_str = LocalizationService.reshape_text("آزمایشگاه اپتیک و توری پراش")
    assert len(fa_str) > 0

    # Digits normalization
    clean_digits = NumericInput.normalize_digits("۱۲۳.۴۵")
    assert clean_digits == "123.45"
    f_val = NumericInput.parse_float("۵۸۹٫۳", default=0.0)
    assert abs(f_val - 589.3) < 1e-4

    # ColorUtils mapping
    rgb_green = ColorUtils.wavelength_to_rgb(546.0)
    assert rgb_green[1] > rgb_green[0] and rgb_green[1] > rgb_green[2], "546nm must be green"
    print("  ✓ Localization, numerals, and font manager verified.")


def test_gui_instantiation_smoke():
    print("[9/9] Testing GUI Smoke Test (MainWindow Initialization)...")
    from ui.main_window import MainWindow

    app = MainWindow()
    # Trigger an angle change
    app.model.set_coarse_angle(19.124)
    app._on_parameter_changed()

    # Verify peak detection
    assert app.centered_peak is not None, "Hg green line should be detected at 19.124°"
    assert "Green" in app.centered_peak.line_name

    # Check tab switching across all 7 tabs
    for tab_id in ["tab_eye", "tab_vern", "tab_2d", "tab_3d", "tab_prof", "tab_calc", "tab_guide"]:
        app.tabview.set(tab_id)
        app._on_tab_changed()

    # Test language toggle
    app._toggle_language()
    assert LocalizationService.get_language() == "en"
    app._toggle_language()
    assert LocalizationService.get_language() == "fa"

    # Test Reset All Parameters
    app.model.set_coarse_angle(120.0)
    app.control_panel.slit_slider.set(0.20)
    app.control_panel._reset_all_parameters()
    assert abs(app.model.effective_telescope_angle - 0.0) < 1e-4, "Angle must reset to 0"
    assert abs(app.control_panel.slit_slider.get() - 0.05) < 0.005, "Slit must reset to 0.05mm"

    # Test Prism mode switch
    app._on_optic_mode_changed("prism")
    assert app.optic_mode == "prism"
    app._on_parameter_changed()
    assert len(app.current_peaks) > 0, "Prism peaks must be computed"

    app.destroy()
    print("  ✓ GUI initialization, reset, and tab switching passed.")


def test_prism_cauchy_physics():
    print("[10/10] Testing Equilateral Glass Prism & Cauchy Dispersion...")
    from physics.prism_engine import PrismEngine
    prism = PrismEngine(apex_angle_deg=60.0, cauchy_A=1.620, cauchy_B_nm2=12500.0)

    # Wavelengths: Violet (404.7 nm) vs Red (656.3 nm)
    n_violet = prism.get_refractive_index(404.656)
    n_red = prism.get_refractive_index(656.280)

    # In glass prism, violet has HIGHER refractive index than red (normal dispersion)
    assert n_violet > n_red, f"Violet n ({n_violet}) must be greater than Red n ({n_red})"

    # Minimum deviation D_min for violet must be GREATER than red
    d_min_violet = prism.calculate_minimum_deviation_deg(404.656)
    d_min_red = prism.calculate_minimum_deviation_deg(656.280)
    assert d_min_violet > d_min_red, f"Violet D_min ({d_min_violet}°) must be greater than Red D_min ({d_min_red}°)"

    # Sodium D-line (589 nm): n ≈ 1.656, D_min ≈ 51.8°
    n_na = prism.get_refractive_index(589.3)
    d_na = prism.calculate_minimum_deviation_deg(589.3)
    assert 1.64 < n_na < 1.67, f"Expected n_Na ~ 1.656, got {n_na}"
    assert 50.0 < d_na < 54.0, f"Expected D_min ~ 51.8°, got {d_na}"
    print("  ✓ Prism Cauchy dispersion and minimum deviation verified.")


def run_all_tests():
    print("=" * 70)
    print("RUNNING COMPLETE SPECTROMETER SIMULATOR TEST SUITE")
    print("=" * 70)

    test_grating_diffraction_angles()
    test_sodium_doublet_and_resolving_power()
    test_hydrogen_balmer_and_rydberg()
    test_vernier_decomposition_and_precision()
    test_kinematics_and_eccentricity_cancellation()
    test_error_models()
    test_exports_docx_and_csv()
    test_localization_and_fonts()
    test_gui_instantiation_smoke()
    test_prism_cauchy_physics()

    print("=" * 70)
    print("ALL 10 TEST SUITES COMPLETED SUCCESSFULLY! (100% PASS)")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
