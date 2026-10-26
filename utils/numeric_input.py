"""
Numeric Input Sanitization and Digits Normalization.
Converts Persian and Arabic digits to ASCII, parses floats safely, and clamps to valid limits.
"""

import re
from typing import Optional, Tuple, Dict, Any

class NumericInput:
    """Safe numeric parser supporting Persian/Arabic numerals and localized decimals."""

    _PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

    @classmethod
    def normalize_digits(cls, text: str) -> str:
        """Converts any Persian or Arabic numerals to standard Latin 0-9."""
        if not text:
            return ""
        # 1. Translate Persian and Arabic-Indic digits
        s = text.translate(cls._PERSIAN_DIGITS)
        # 2. Standardize Persian decimal slash / momayyez
        s = s.replace("٫", ".").replace("،", "").replace(",", "")
        # 3. Strip BiDi marks and spaces
        s = re.sub(r"[‎‏‪-‮\s]", "", s)
        return s

    @classmethod
    def parse_float(
        cls,
        text: str,
        default: float = 0.0,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> float:
        """
        Parses string to float, applying digit normalization and bounds clamping.
        """
        clean = cls.normalize_digits(text)
        try:
            val = float(clean)
        except (ValueError, TypeError):
            val = default

        if min_val is not None:
            val = max(min_val, val)
        if max_val is not None:
            val = min(max_val, val)

        return val

    @classmethod
    def parse_int(
        cls,
        text: str,
        default: int = 0,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None
    ) -> int:
        """
        Parses string to integer, applying digit normalization and bounds clamping.
        """
        clean = cls.normalize_digits(text)
        try:
            val = int(round(float(clean)))
        except (ValueError, TypeError):
            val = default

        if min_val is not None:
            val = max(min_val, val)
        if max_val is not None:
            val = min(max_val, val)

        return val
