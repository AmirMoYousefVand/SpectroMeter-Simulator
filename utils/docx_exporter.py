"""
Microsoft Word (.docx) Laboratory Report Exporter with Native OMML Equations.
Exports professional scientific reports matching laboratory optical standards:
- Native Microsoft Office Math (OMML) blocks (<m:oMath>) rendered natively in Word equation editor
- Theoretical derivations of Fraunhofer diffraction and N-slit interference
- Apparatus specifications and alignment parameters
- Experimental observations table with dual Vernier readings and error analysis
- Hydrogen Balmer series and Rydberg constant calculations
"""

import os
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from physics.spectrometer_model import SpectrometerModel
from physics.grating_engine import GratingEngine
from physics.constants import SpectralSource, RYDBERG_CONSTANT_H

class DocxEquationExporter:
    """Generates professional scientific laboratory reports in Word format with native math equations."""

    @staticmethod
    def _add_omml_equation(paragraph, omml_inner_xml: str):
        """Appends a native Microsoft Office Math (OMML) block into a python-docx paragraph."""
        ns = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
        full_xml = f'<m:oMathPara {ns}><m:oMath>{omml_inner_xml}</m:oMath></m:oMathPara>'
        element = parse_xml(full_xml)
        paragraph._p.append(element)

    @classmethod
    def export_report(
        cls,
        filepath: str,
        model: SpectrometerModel,
        grating_engine: GratingEngine,
        source: SpectralSource,
        measurements: List[Dict[str, Any]],
        is_persian: bool = True
    ):
        """
        Builds and saves the complete laboratory report into a .docx document.
        """
        doc = Document()

        # Set 0.8-inch margins
        for s in doc.sections:
            s.top_margin = Inches(0.8)
            s.bottom_margin = Inches(0.8)
            s.left_margin = Inches(0.9)
            s.right_margin = Inches(0.9)

        # Scientific Palette
        col_primary = RGBColor(14, 116, 144)    # Deep Cyan
        col_secondary = RGBColor(51, 65, 85)   # Slate 700
        col_accent = RGBColor(180, 83, 9)      # Warm Amber

        # ----------------------------------------------------------------------
        # 1. Document Title & Metadata Header
        # ----------------------------------------------------------------------
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_text = "گزارش آزمایش اسپکترومتر اپتیکی و توری پراش" if is_persian else "Optical Spectrometer & Diffraction Grating Laboratory Report"
        run_title = title_p.add_run(title_text)
        run_title.font.name = "Arial"
        run_title.font.size = Pt(20)
        run_title.font.bold = True
        run_title.font.color.rgb = col_primary

        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_text = "آزمایشگاه اپتیک موجی و فیزیک مدرن — دانشگاه" if is_persian else "Wave Optics & Modern Physics Laboratory"
        run_sub = sub_p.add_run(sub_text)
        run_sub.font.name = "Arial"
        run_sub.font.size = Pt(12)
        run_sub.font.color.rgb = col_secondary

        date_p = doc.add_paragraph()
        date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_date = date_p.add_run(datetime.now().strftime("%Y-%m-%d  %H:%M"))
        run_date.font.name = "Arial"
        run_date.font.size = Pt(9)
        run_date.font.italic = True
        run_date.font.color.rgb = RGBColor(120, 120, 120)

        doc.add_paragraph() # Spacer

        # ----------------------------------------------------------------------
        # 2. Apparatus Specifications Table
        # ----------------------------------------------------------------------
        h1 = doc.add_paragraph()
        r_h1 = h1.add_run("۱. کالبدشکافی و مشخصات دستگاه اسپکترومتر" if is_persian else "1. Apparatus Specifications")
        r_h1.font.size = Pt(14)
        r_h1.font.bold = True
        r_h1.font.color.rgb = col_primary

        spec_table = doc.add_table(rows=6, cols=2)
        spec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        spec_table.autofit = False

        specs = [
            ("چشمه نوری گسیلی (Light Source)" if is_persian else "Spectral Light Source", f"{source.name_fa} ({source.name_en})"),
            ("ثابت گام توری (Grating Constant d)" if is_persian else "Grating Constant (d)", f"{grating_engine.d_nm:.2f} nm  ({grating_engine.lines_per_mm:.0f} lines/mm)"),
            ("پهنای باریکه روشن‌شده (Illuminated Beam)" if is_persian else "Illuminated Width", f"{grating_engine.beam_width_mm:.1f} mm  (N_total ≈ {grating_engine.illuminated_lines_Nt:.0f} lines)"),
            ("فاصله کانونی کولیماتور و شیئی (Focal Lengths)" if is_persian else "Lens Focal Lengths", "f_coll = 178 mm , f_tele = 178 mm"),
            ("دقت قرائت دایره مدرج و ورنیه (Vernier Precision)" if is_persian else "Vernier Precision", "1' (One Arcminute = 1/60°)"),
            ("فاصله زاویه‌ای دو ورنیه (Vernier Separation)" if is_persian else "Dual Vernier Separation", "180° Diametrically Opposite"),
        ]

        for i, (param, val) in enumerate(specs):
            row = spec_table.rows[i]
            row.cells[0].text = param
            row.cells[1].text = val
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
            row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)

        doc.add_paragraph()

        # ----------------------------------------------------------------------
        # 3. Theoretical Derivations & OMML Math Equations
        # ----------------------------------------------------------------------
        h2 = doc.add_paragraph()
        r_h2 = h2.add_run("۲. روابط فیزیکی حاکم بر توری پراش" if is_persian else "2. Mathematical Foundations & Equations")
        r_h2.font.size = Pt(14)
        r_h2.font.bold = True
        r_h2.font.color.rgb = col_primary

        p_eq1 = doc.add_paragraph()
        p_eq1.add_run("معادله اصلی توری پراش (شرط تداخل سازنده):" if is_persian else "Primary Diffraction Grating Equation:")
        # OMML: d * sin(θ_m) = m * λ
        omml_1 = (
            '<m:r><m:t>d</m:t></m:r>'
            '<m:r><m:t>·</m:t></m:r>'
            '<m:r><m:t>sin</m:t></m:r>'
            '<m:sSub><m:e><m:r><m:t>(θ</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>'
            '<m:r><m:t>)</m:t></m:r>'
            '<m:r><m:t>=</m:t></m:r>'
            '<m:r><m:t>m</m:t></m:r>'
            '<m:r><m:t>·λ</m:t></m:r>'
            '<m:r><m:t>   ⟹   λ = </m:t></m:r>'
            '<m:f><m:num><m:r><m:t>d·sin(θ)</m:t></m:r></m:num><m:den><m:r><m:t>m</m:t></m:r></m:den></m:f>'
        )
        cls._add_omml_equation(p_eq1, omml_1)

        p_eq2 = doc.add_paragraph()
        p_eq2.add_run("توان تفکیک توری بر اساس معیار ریلی:" if is_persian else "Resolving Power (Rayleigh Criterion):")
        # OMML: R = λ / Δλ = m * N_t
        omml_2 = (
            '<m:r><m:t>R = </m:t></m:r>'
            '<m:f><m:num><m:r><m:t>λ</m:t></m:r></m:num><m:den><m:r><m:t>Δλ</m:t></m:r></m:den></m:f>'
            '<m:r><m:t> = |m|·</m:t></m:r>'
            '<m:sSub><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>total</m:t></m:r></m:sub></m:sSub>'
        )
        cls._add_omml_equation(p_eq2, omml_2)

        if source.id == "H":
            p_eq3 = doc.add_paragraph()
            p_eq3.add_run("رابطه سری بالمر هیدروژن و ثابت ریدبرگ:" if is_persian else "Balmer Series & Rydberg Constant:")
            # OMML: 1 / λ = R_H * (1/4 - 1/n^2)
            omml_3 = (
                '<m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>λ</m:t></m:r></m:den></m:f>'
                '<m:r><m:t> = </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>H</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t>·(</m:t></m:r>'
                '<m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>4</m:t></m:r></m:den></m:f>'
                '<m:r><m:t> - </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:sSup><m:e><m:r><m:t>n</m:t></m:r></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup></m:den></m:f>'
                '<m:r><m:t>)</m:t></m:r>'
            )
            cls._add_omml_equation(p_eq3, omml_3)

        doc.add_paragraph()

        # ----------------------------------------------------------------------
        # 4. Experimental Measurements Table
        # ----------------------------------------------------------------------
        h3 = doc.add_paragraph()
        r_h3 = h3.add_run("۳. جدول داده‌های اندازه‌گیری آزمایشگاهی" if is_persian else "3. Experimental Observations Table")
        r_h3.font.size = Pt(14)
        r_h3.font.bold = True
        r_h3.font.color.rgb = col_primary

        if not measurements:
            p_empty = doc.add_paragraph()
            p_empty.add_run("(هیچ داده‌ای در جدول ثبت نشده است)" if is_persian else "(No measurements recorded)")
        else:
            table = doc.add_table(rows=len(measurements) + 1, cols=8)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            headers = [
                "ردیف" if is_persian else "#",
                "نام خط" if is_persian else "Line",
                "مرتبه" if is_persian else "Order",
                "ورنیه ۱" if is_persian else "Vernier 1",
                "ورنیه ۲" if is_persian else "Vernier 2",
                "زاویه انحراف" if is_persian else "Dev Angle",
                "طول‌موج محاسباتی" if is_persian else "λ Calc (nm)",
                "درصد خطا" if is_persian else "Error %"
            ]

            hdr_cells = table.rows[0].cells
            for j, h_text in enumerate(headers):
                hdr_cells[j].text = h_text
                hdr_cells[j].paragraphs[0].runs[0].font.bold = True
                hdr_cells[j].paragraphs[0].runs[0].font.size = Pt(9)
                # Background color for header
                shading = parse_xml(r'<w:shd {} w:fill="0E7490"/>'.format(nsdecls('w')))
                hdr_cells[j]._tc.get_or_add_tcPr().append(shading)
                hdr_cells[j].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

            for i, row_data in enumerate(measurements):
                row_cells = table.rows[i + 1].cells
                row_cells[0].text = str(row_data["index"])
                row_cells[1].text = str(row_data["line_name"])
                row_cells[2].text = f"m={row_data['order_m']}"
                row_cells[3].text = str(row_data["v1_str"])
                row_cells[4].text = str(row_data["v2_str"])
                row_cells[5].text = f"{row_data['dev_deg']:.2f}°"
                row_cells[6].text = f"{row_data['calc_wl_nm']:.2f}"
                row_cells[7].text = f"{row_data['error_percent']:.2f}%"

                for c in row_cells:
                    c.paragraphs[0].runs[0].font.size = Pt(8.5)

        doc.add_paragraph()

        # ----------------------------------------------------------------------
        # 5. Error Analysis & Conclusion
        # ----------------------------------------------------------------------
        h4 = doc.add_paragraph()
        r_h4 = h4.add_run("۴. تحلیل خطا و نتیجه‌گیری" if is_persian else "4. Error Analysis & Conclusion")
        r_h4.font.size = Pt(14)
        r_h4.font.bold = True
        r_h4.font.color.rgb = col_primary

        conc_p = doc.add_paragraph()
        conc_text = (
            "۱. میانگین‌گیری از قرائت‌های دو ورنیه متقابل (۱۸۰ درجه) خطای ناشی از عدم انطباق محور چرخش با مرکز دایره مدرج (Eccentricity Error) را حذف می‌کند.\n"
            "۲. رابطه خطای نسبی محاسبه طول‌موج از بسط دیفرانسیلی به دست می‌آید:\n"
            "   Δλ / λ = Δd / d + cot(θ) · Δθ\n"
            "۳. تراز بودن سطح توری با پیچ‌های سه‌گانه زیر میز تضمین می‌کند که خطوط طیفی عمود بر رتیکول باقی مانده و زوایای انحراف در دو سمت متقارن باشند."
        ) if is_persian else (
            "1. Averaging readings from both diametrically opposite Verniers (V1 and V2) eliminates pivot eccentricity error.\n"
            "2. Relative wavelength measurement error formula: Δλ / λ = Δd / d + cot(θ) · Δθ.\n"
            "3. Proper table leveling via Schuster's method ensures symmetrical deviations and eliminates slit slant."
        )
        conc_p.add_run(conc_text)

        # Save document
        doc.save(filepath)
