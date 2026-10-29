"""
User Guide, Theory Manual & Schuster's Alignment Tutorial View (راهنمای آزمایش و روش شوستر).
Provides comprehensive bilingual documentation on spectrometer anatomy, Schuster leveling method,
vernier 1-arcminute reading instructions, and experiment procedures for Hg, Na, and H lamps.
"""

import customtkinter as ctk
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class GuideView(ctk.CTkScrollableFrame):
    """
    Scrollable textbook and laboratory operation manual.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()
        font_h2 = FontManager.get_ui_font(13, "bold", is_fa)
        font_body = FontManager.get_ui_font(11, "normal", is_fa)

        self.sections = [
            {
                "title_en": "1. Anatomy of the Laboratory Spectrometer",
                "title_fa": "۱. کالبدشکافی و اجزای اصلی دستگاه اسپکترومتر",
                "body_en": [
                    "An optical spectrometer consists of four fundamental coaxial subsystems:",
                    "• Collimator: Fixed tube with an adjustable entrance slit at the focus of an achromatic lens, converting divergent light from the lamp into parallel rays (plane waves) required for Fraunhofer diffraction.",
                    "• Central Prism/Grating Table: Circular rotating stage with three leveling thumbscrews at 120° for orienting the diffraction grating plane perpendicular to the optical axis.",
                    "• Telescope: Rotatable tube with an achromatic objective lens and an eyepiece containing fine crosshairs (reticle). Collects diffracted parallel rays and focuses spectral slit images onto the reticle.",
                    "• Graduated Circular Scale & Verniers: Precision 360° disk divided into 30 arcminute (0.5°) intervals, equipped with two diametrically opposite Verniers (V₁ and V₂) reading to 1 arcminute (1')."
                ],
                "body_fa": [
                    "دستگاه اسپکترومتر آزمایشگاهی از چهار بخش اصلی هم‌محور تشکیل شده است:",
                    "• کولیماتور یا موازی‌ساز: لوله فلزی ثابت مجهز به شکاف ورودی میکرومتری در کانون عدسی شیئی که پرتوهای واگرای چشمه نور را به باریکه موازی با جبهه‌موج تخت تبدیل می‌کند.",
                    "• میز مرکزی توری: صفحه گردان دارای سه پیچ تراز با فواصل ۱۲۰ درجه که توری پراش را دقیقاً عمود بر محور اپتیکی دستگاه نگه می‌دارد.",
                    "• تلسکوپ: سامانه اپتیکی چرخان حول محور مرکزی که پرتوهای پراش‌یافته را جمع‌آوری کرده و تصویر حقیقی شکاف را روی تارعنکبوتی (رتیکول) متمرکز می‌کند.",
                    "• دایره مدرج و ورنیه‌ها: صفحه مدور ۳۶۰ درجه مدرج به فواصل ۳۰ دقیقه قوسی (نیم‌درجه) به همراه دو ورنیه دوطرفه با دقت ۱ دقیقه قوسی."
                ]
            },
            {
                "title_en": "2. Schuster's Alignment Method",
                "title_fa": "۲. روش تراز کردن و فوکوس دستگاه (روش شوستر)",
                "body_en": [
                    "Schuster's method is the standard optical procedure to focus both the collimator and telescope for parallel light (infinity focus) without taking the instrument outdoors:",
                    "Step 1: Eyepiece Focus — Rotate the eyepiece tube until the crosshairs (reticle wires) appear perfectly sharp and black.",
                    "Step 2: Table Leveling — Illuminate with a mercury lamp. Rotate the telescope to observe the diffracted slit images on both the right and left sides. If the slit tilts or drifts vertically, adjust the three leveling screws beneath the central table until the center of the slit bisects the horizontal reticle line symmetrically across all angles.",
                    "Step 3: Collimator Slit Width — Adjust the entrance slit micrometer knob to obtain sharp, well-resolved spectral lines without excessive diffraction line broadening."
                ],
                "body_fa": [
                    "روش شوستر روش استاندارد آزمایشگاهی برای فوکوس تلسکوپ و موازی‌ساز روی بی‌نهایت بدون نیاز به نشانه‌گیری اجسام دوردست است:",
                    "مرحله ۱: فوکوس چشمی — لوله چشمی را آنقدر تنظیم کنید تا خطوط تارعنکبوتی کاملاً سیاه، تیز و بدون خستگی چشم دیده شوند.",
                    "مرحله ۲: تراز کردن میز توری — با مشاهده خطوط در زوایای چپ و راست، پیچ‌های سه‌گانه زیر میز را تنظیم کنید تا تصویر شکاف کاملاً عمود و متقارن در مرکز خط افقی رتیکول قرار گیرد.",
                    "مرحله ۳: پهنای شکاف — پیچ میکرومتری شکاف کولیماتور را به گونه‌ای تنظیم کنید که خطوط به اندازه کافی باریک و تفکیک‌شده باشند بدون اینکه شدت نور بیش از حد افت کند."
                ]
            },
            {
                "title_en": "3. How to Read the Vernier Scale with 1 Arcminute Precision",
                "title_fa": "۳. راهنمای خواندن ورنیه با دقت ۱ دقیقه قوسی",
                "body_en": [
                    "The main circular scale has divisions of 30 arcminutes (0.5°).",
                    "The Vernier plate has 30 subdivisions spanning 29 main scale divisions.",
                    "Least Count (LC) = 30' / 30 = 1 arcminute (1' = 1/60°).",
                    "Formula: Angle = MSR (Main Scale Reading) + VSR (Vernier Scale Reading)",
                    "1. Find the zero mark of the Vernier: Note the last main scale line it has passed (e.g., 21° 00' or 21° 30'). This is MSR.",
                    "2. Look through the magnifier loupe: Scan along the Vernier lines (0 to 29) to find the ONE line that aligns perfectly with a main scale line. This line index is VSR in arcminutes.",
                    "3. Add VSR to MSR: e.g., 21° 30' + 14' = 21° 44'.",
                    "4. Read Vernier 2 (opposite side) and average them to eliminate mechanical eccentricity error!"
                ],
                "body_fa": [
                    "دایره مدرج اصلی به فواصل نیم‌درجه (۳۰ دقیقه قوسی) تقسیم شده است.",
                    "ورنیه دارای ۳۰ تقسیم‌بندی است که دقیقاً برابر با ۲۹ تقسیم دایره اصلی است.",
                    "دقت دستگاه (Least Count) = ۳۰ دقیقه تقسیم بر ۳۰ = ۱ دقیقه قوسی.",
                    "فرمول قرائت: زاویه = خط مقیاس اصلی (MSR) + خط منطبق ورنیه (VSR)",
                    "۱. صفر ورنیه را بیابید: ببینید از کدام خط دایره مدرج رد شده است (مثلاً ۲۱° ۰۰' یا ۲۱° ۳۰'). این مقدار MSR است.",
                    "۲. از درون ذره‌بین، خطوط ورنیه (۰ تا ۲۹) را بررسی کنید و خطی را که دقیقاً با یکی از خطوط دایره اصلی هم‌راستاست پیدا کنید. این عدد VSR به دقیقه قوسی است.",
                    "۳. مجموع: ۲۱° ۳۰' به علاوه ۱۴' می‌شود ۲۱° ۴۴'.",
                    "۴. ورنیه دوم در سمت مقابل (۱۸۰ درجه) را نیز بخوانید و برای حذف خطای خروج از مرکز میانگین بگیرید!"
                ]
            },
            {
                "title_en": "4. Laboratory Experiments & Formulas",
                "title_fa": "۴. دستورکار آزمایش‌های آزمایشگاه و فرمول‌های حاکم",
                "body_en": [
                    "• Experiment A: Grating Constant & Unknown Wavelengths (Mercury Lamp):",
                    "  Using known green line (546.07 nm), verify grating constant d = m·λ / sin(θ). Then measure angles for yellow, blue, and violet lines to calculate unknown wavelengths.",
                    "• Experiment B: Resolving Power of Sodium Doublet (Na D-Lines):",
                    "  Observe the two closely spaced yellow lines at 589.0 nm and 589.6 nm (Δλ = 0.6 nm). Verify Rayleigh criterion R = λ / Δλ = m·N_t.",
                    "• Experiment C: Hydrogen Balmer Series & Rydberg Constant R_H:",
                    "  Measure diffraction angles for H-alpha (656.3 nm), H-beta (486.1 nm), H-gamma (434.0 nm). Compute experimental Rydberg constant R_H = 1 / [λ (0.25 - 1/n²)] and verify against CODATA value 1.097373 × 10⁷ m⁻¹."
                ],
                "body_fa": [
                    "• آزمایش الف: تعیین ثابت توری و طول‌موج‌های مجهول (لامپ جیوه):",
                    "  با استفاده از خط سبز معلوم (۵۴۶.۰۷ نانومتر)، ثابت توری را از رابطه d = m·λ / sin(θ) بسنجید. سپس با خواندن زوایای خطوط زرد، آبی و بنفش، طول‌موج‌های مجهول را حساب کنید.",
                    "• آزمایش ب: بررسی توان تفکیک خطوط دوتایی سدیم (خطوط D):",
                    "  مشاهده دو خط دوتایی بسیار نزدیک زرد در ۵۸۹.۰ و ۵۸۹.۶ نانومتر (اختلاف ۰.۶ نانومتر) و بررسی برقراری معیار تفکیک ریلی R = λ / Δλ = m·N_t.",
                    "• آزمایش ج: سری بالمر هیدروژن و تعیین تجربی ثابت ریدبرگ:",
                    "  اندازه‌گیری زوایای خطوط H-alpha، H-beta و H-gamma و محاسبه ثابت ریدبرگ از رابطه 1/λ = R_H (1/4 - 1/n²) و مقایسه با مقدار تئوری ۱.۰۹۷۳۷۳ × ۱۰⁷ بر متر."
                ]
            }
        ]

        self.cards = []
        for s_idx, sec in enumerate(self.sections):
            card = ctk.CTkFrame(self, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A38")
            card.grid(row=s_idx, column=0, sticky="ew", padx=8, pady=6)
            card.grid_columnconfigure(0, weight=1)

            t_txt = sec["title_fa"] if is_fa else sec["title_en"]
            lbl_title = ctk.CTkLabel(card, text=t_txt, font=font_h2, text_color="#38BDF8")
            lbl_title.grid(row=0, column=0, sticky="e" if is_fa else "w", padx=12, pady=(8, 4))

            body_lines = sec["body_fa"] if is_fa else sec["body_en"]
            line_lbls = []
            for l_idx, line in enumerate(body_lines):
                lbl_line = ctk.CTkLabel(
                    card,
                    text=line,
                    font=font_body,
                    text_color="#E2E8F0",
                    wraplength=760,
                    justify="right" if is_fa else "left"
                )
                lbl_line.grid(row=l_idx + 1, column=0, sticky="e" if is_fa else "w", padx=16, pady=2)
                line_lbls.append(lbl_line)

            self.cards.append({"title": lbl_title, "lines": line_lbls, "data": sec})

    def refresh_language(self):
        """Refreshes text and alignment when language changes."""
        is_fa = LocalizationService.is_persian()
        font_h2 = FontManager.get_ui_font(13, "bold", is_fa)
        font_body = FontManager.get_ui_font(11, "normal", is_fa)

        for card in self.cards:
            sec = card["data"]
            t_txt = sec["title_fa"] if is_fa else sec["title_en"]
            card["title"].configure(text=t_txt, font=font_h2)
            card["title"].grid(sticky="e" if is_fa else "w")

            body_lines = sec["body_fa"] if is_fa else sec["body_en"]
            for lbl, text in zip(card["lines"], body_lines):
                lbl.configure(text=text, font=font_body, justify="right" if is_fa else "left")
                lbl.grid(sticky="e" if is_fa else "w")
