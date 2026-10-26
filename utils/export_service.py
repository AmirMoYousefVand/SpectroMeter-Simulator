"""
Export Service Coordinator for CSV datasets and high-resolution figure outputs.
"""

import csv
from typing import List, Dict, Any
from matplotlib.figure import Figure

class ExportService:
    """Handles multi-format scientific dataset and graphic exports."""

    @staticmethod
    def export_csv(filepath: str, measurements: List[Dict[str, Any]]):
        """
        Exports laboratory observations to a CSV file encoded in utf-8-sig (with BOM),
        ensuring perfect display of Persian text, degree symbols, and Greek letters in Microsoft Excel.
        """
        fieldnames = [
            "Index",
            "Line_Name",
            "Order_m",
            "Vernier_1_Readout",
            "Vernier_2_Readout",
            "Corrected_Angle_deg",
            "Deviation_Angle_deg",
            "Calculated_Wavelength_nm",
            "True_Wavelength_nm",
            "Relative_Error_Percent"
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)

            for m in measurements:
                writer.writerow([
                    m.get("index", ""),
                    m.get("line_name", ""),
                    m.get("order_m", ""),
                    m.get("v1_str", ""),
                    m.get("v2_str", ""),
                    f"{m.get('corr_deg', 0.0):.3f}",
                    f"{m.get('dev_deg', 0.0):.3f}",
                    f"{m.get('calc_wl_nm', 0.0):.2f}",
                    f"{m.get('true_wl_nm', 0.0):.2f}",
                    f"{m.get('error_percent', 0.0):.2f}"
                ])

    @staticmethod
    def export_figure(fig: Figure, filepath: str, dpi: int = 300):
        """Saves Matplotlib figure to publication-quality PNG, PDF, or SVG."""
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
