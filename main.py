"""
Entry Point for Optical Spectrometer & Diffraction Grating Simulator.
"""

import sys
import os
import traceback
import tempfile
from datetime import datetime

# Reconfigure Windows stdout/stderr to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Bind Windows Taskbar AppUserModelID to display custom icon
if sys.platform.startswith("win"):
    try:
        import ctypes
        app_id = "spectrometer.simulator.optical.goniometer.v1_0_0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def report_fatal_error(exc: Exception):
    """Logs fatal startup crashes to temporary log file."""
    log_path = os.path.join(tempfile.gettempdir(), "spectrometer_simulator_error.log")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- FATAL ERROR: {datetime.now()} ---\n")
            traceback.print_exc(file=f)
        print(f"Critical error logged to: {log_path}")
    except Exception:
        pass

def main():
    """Initializes and runs the main spectrometer desktop application."""
    try:
        from utils.font_manager import FontManager
        FontManager.initialize()

        from ui.main_window import MainWindow
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nSpectrometer Simulator terminated by user.")
    except Exception as e:
        report_fatal_error(e)
        raise e

if __name__ == "__main__":
    main()
