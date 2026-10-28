# High-Precision Optical Spectrometer & Diffraction Grating Simulator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform Windows](https://img.shields.io/badge/platform-Windows%2064--bit-0078D6.svg)](https://github.com/AmirMoYousefVand/SpectroMeter-Simulator)
[![GUI CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-10B981.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Release v1.1.0](https://img.shields.io/badge/release-v1.1.0-cyan.svg)](https://github.com/AmirMoYousefVand/SpectroMeter-Simulator/releases/tag/v1.1.0)

> **[مطالعه راهنمای کامل به زبان فارسی (Persian Documentation)](README.fa.md)**

A high-fidelity, research-grade desktop simulator of an optical spectrometer and goniometer equipped with diffraction gratings and equilateral glass prisms. Engineered for university wave optics laboratories, physics departments, and optical metrology instruction.

---

## Table of Contents
- [Key Features](#key-features)
- [Mathematical & Physical Foundation](#mathematical--physical-foundation)
  - [1. Fraunhofer Diffraction & N-Slit Interference](#1-fraunhofer-diffraction--n-slit-interference)
  - [2. Absent Spectra (Missing Orders)](#2-absent-spectra-missing-orders)
  - [3. Resolving Power & Rayleigh Criterion](#3-resolving-power--rayleigh-criterion)
  - [4. Angular Dispersion](#4-angular-dispersion)
  - [5. Equilateral Prism Refraction & Cauchy Dispersion](#5-equilateral-prism-refraction--cauchy-dispersion)
  - [6. Hydrogen Balmer Series & Rydberg Constant](#6-hydrogen-balmer-series--rydberg-constant)
  - [7. Dual Vernier Scale & Eccentricity Cancellation](#7-dual-vernier-scale--eccentricity-cancellation)
  - [8. Defocus Blur & Schuster Table Alignment](#8-defocus-blur--schuster-table-alignment)
- [Apparatus Anatomy & View Tabs](#apparatus-anatomy--view-tabs)
- [Interactive Controls & Shortcuts](#interactive-controls--shortcuts)
- [Laboratory Report Generation](#laboratory-report-generation)
- [Installation & Running](#installation--running)
  - [Option A: Portable Windows Executable](#option-a-portable-windows-executable-recommended)
  - [Option B: Running from Source](#option-b-running-from-source)
- [Building Standalone Executable](#building-standalone-executable)
- [License](#license)

---

## Key Features

- **Physical Apparatus Modeling**: Realistic circular main scale ($360^\circ$ divided into $30'$ intervals), rotating collimator and telescope arms, table leveling screws, fine micrometer tangent screw ($\pm 5^\circ$), and locking clamp.
- **Dual Magnified Vernier Loupes**: Independent Vernier 1 and Vernier 2 reading plates with $1'$ ($1/60^\circ$) Least Count. Supports mouse dragging, mouse wheel micro-stepping, step buttons (`[-1°]`, `[-10']`, `[-1']`, `[+1']`, `[+10']`, `[+1°]`), and digital reading breakdowns.
- **Complete Discharge Lamp Spectra**: Mercury (Hg), Sodium Doublet (Na D1/D2 at $589.0\text{ nm}$ and $589.6\text{ nm}$), Hydrogen Balmer Series ($H_\alpha, H_\beta, H_\gamma, H_\delta$), Helium (He), Neon (Ne), Continuous White Light with discrete color markers, Monochromatic Laser, and Custom Spectral Line definition.
- **Equilateral Glass Prism Mode**: Seamless toggle between diffraction grating and equilateral flint glass prism ($A = 60^\circ$) with Cauchy dispersion relation and minimum deviation angle ($D_{\min}$) measurements.
- **Instrumental & Alignment Systematic Errors**: Defocus Point Spread Function (PSF) line broadening, Schuster optical leveling tilt (vertical crosshair drift and slit slant), and goniometer axis eccentricity.
- **Interactive Unknown Element Quiz**: Blind spectroscopy mode challenging students to observe unlabelled spectral lines, compute experimental wavelengths, and identify unknown gas discharge lamps.
- **Darkroom Lighting Mode**: Ambient darkroom mode with dimmed UI and high-contrast glowing optical paths for authentic laboratory observation.
- **Bilingual Interface**: Native Persian (فارسی) and English support with authentic typography (Vazirmatn and Space Grotesk) and dynamic RTL/LTR layout management.
- **Automated Report Exports**: Professional Word (`.docx`) lab reports with native Microsoft Office Math (OMML `<m:oMath>`) blocks and UTF-8-SIG CSV observation worksheets.

---

## Mathematical & Physical Foundation

### 1. Fraunhofer Diffraction & N-Slit Interference
For a transmission diffraction grating with groove period $d = 1 / N_{lines}$ at oblique incidence angle $\theta_i$, principal diffraction maxima occur at angles $\theta_m$ satisfying the grating equation:

$$d (\sin\theta_m - \sin\theta_i) = m \lambda \quad (m = 0, \pm 1, \pm 2, \dots)$$

The angular intensity profile $I(\theta)$ is governed by single-groove diffraction modulated by $N$-slit interference:

$$I(\theta) = I_0 \left( \frac{\sin\beta}{\beta} \right)^2 \left( \frac{\sin(N_t \gamma)}{\sin\gamma} \right)^2$$

Where:
$$\beta = \frac{\pi a}{\lambda} (\sin\theta - \sin\theta_i), \quad \gamma = \frac{\pi d}{\lambda} (\sin\theta - \sin\theta_i)$$
- $a$: transparent groove aperture width ($a < d$).
- $N_t$: number of illuminated grating lines ($N_t = W_{beam} \cdot N_{lines}$).

### 2. Absent Spectra (Missing Orders)
When a diffraction grating principal maximum coincides exactly with a single-groove diffraction zero, that diffraction order is extinguished:

$$d \sin\theta = m \lambda \quad \text{and} \quad a \sin\theta = p \lambda \implies \frac{m}{p} = \frac{d}{a}$$

When the ratio $d/a = k$ is an integer (e.g., $d/a = 2$ for equal opaque and transparent rulings), orders $m = \pm 2, \pm 4, \dots$ completely vanish.

### 3. Resolving Power & Rayleigh Criterion
Two adjacent spectral lines of wavelengths $\lambda$ and $\lambda + \Delta\lambda$ are barely resolved according to Rayleigh's criterion when the principal maximum of one line coincides with the first interference minimum of the second:

$$R = \frac{\lambda}{\Delta\lambda_{\min}} = |m| N_t = |m| \cdot \left( \frac{W_{beam}}{d} \right)$$

For the Sodium D-doublet ($\lambda_1 = 589.00\text{ nm}, \lambda_2 = 589.59\text{ nm}, \Delta\lambda = 0.59\text{ nm}$):
$$R_{required} = \frac{589.3}{0.59} \approx 998$$
A 600 lines/mm grating illuminated by a 15 mm beam provides $N_t = 9000$ lines, yielding $R = 9000$ in order $m=1$, resolving the doublet with wide margin.

### 4. Angular Dispersion
The rate of angular separation per unit wavelength change:

$$D = \frac{d\theta}{d\lambda} = \frac{m}{d \cos\theta_m}$$

Angular dispersion increases with diffraction order $m$, groove density $1/d$, and diffraction angle $\theta_m$.

### 5. Equilateral Prism Refraction & Cauchy Dispersion
For an equilateral glass prism with apex angle $A = 60^\circ$, total angular deviation $\delta$ is minimized when light traverses the prism symmetrically ($i_1 = i_2, r_1 = r_2 = A/2 = 30^\circ$):

$$n = \frac{\sin\left(\frac{A + D_{\min}}{2}\right)}{\sin\left(\frac{A}{2}\right)} = 2 \sin\left(30^\circ + \frac{D_{\min}}{2}\right)$$

The refractive index $n(\lambda)$ follows Cauchy's empirical dispersion formula for flint glass:

$$n(\lambda) = A_{Cauchy} + \frac{B_{Cauchy}}{\lambda^2}$$

Inverting Cauchy's relation allows computing experimental wavelengths from measured deviations:

$$\lambda_{\text{calc}} = \sqrt{\frac{B_{Cauchy}}{n_{\text{calc}} - A_{Cauchy}}}$$

### 6. Hydrogen Balmer Series & Rydberg Constant
For the Hydrogen discharge lamp, visible transitions from upper quantum levels $n \in \{3, 4, 5, 6\}$ to $n_1 = 2$ follow the Balmer-Rydberg formula:

$$\frac{1}{\lambda} = R_H \left( \frac{1}{2^2} - \frac{1}{n^2} \right) = R_H \left( 0.25 - \frac{1}{n^2} \right)$$

By measuring the diffraction angle $\theta$ for $H_\alpha (656.28\text{ nm}, n=3)$, $H_\beta (486.13\text{ nm}, n=4)$, $H_\gamma (434.05\text{ nm}, n=5)$, and $H_\delta (410.17\text{ nm}, n=6)$, the experimental Rydberg constant is extracted:

$$R_{H,\text{exp}} = \frac{1}{\lambda_{\text{exp}} \left( 0.25 - \frac{1}{n^2} \right)}$$

### 7. Dual Vernier Scale & Eccentricity Cancellation
The circular main scale is graduated in degrees with subdivisions every $30'$ ($0.5^\circ$). The Vernier plate spans 29 main scale divisions divided into 30 equal subdivisions, giving a Least Count (LC):

$$\text{LC} = 1 \text{ MSD} - 1 \text{ VSD} = 30' - \frac{29 \times 30'}{30} = 1 \text{ arcminute} = \frac{1}{60}^\circ$$

Total angle reading for each Vernier:
$$\theta = \text{MSR} + (\text{VSR} \times 1')$$

Mechanical axis misalignment between the scale circle center and goniometer pivot induces periodic eccentricity error:
$$\delta\theta_{\text{ecc}} = \frac{e}{R} \sin(\theta - \phi_0)$$

Because Vernier 1 and Vernier 2 are positioned diametrically opposite ($180^\circ$ apart), circular averaging cancels eccentricity error to first order:

$$\theta_{\text{corrected}} = \text{circular\_mean}(\theta_{V1}, \theta_{V2} - 180^\circ)$$

### 8. Defocus Blur & Schuster Table Alignment
- **Focus Blur**: Point Spread Function (PSF) Gaussian convolution broadening:
  $$\sigma_{\text{blur}} = \sigma_0 \cdot \left[ 1 + k_f \left( |F_{coll} - 50| + |F_{tele} - 50| \right) \right]$$
- **Schuster Table Tilt**: Grating plane tilt angles $(\alpha_x, \alpha_y)$ cause crosshair vertical drift and spectral slit slant:
  $$\Delta y = f_{tele} \cdot \alpha_x \sin\theta, \quad \Delta\phi_{\text{slant}} = \alpha_y \cos\theta$$

---

## Apparatus Anatomy & View Tabs

| Tab | Title | Description |
|:---:|:---|:---|
| **1** | **Eyepiece View (نمای چشمی)** | High-magnification circular ocular reticle with crosshairs, spectral lines, defocus blur, tilt slant, and ambient darkroom mode. |
| **2** | **Dual Verniers (ورنیه‌های دوطرفه)** | High-resolution interactive brass loupes for Vernier 1 and Vernier 2 with mouse drag, mouse wheel micro-stepping, step buttons, and digital decomposition breakdown. |
| **3** | **2D Optical Setup (چیدمان دوبعدی)** | Top-down schematic ray diagram showing light source, collimator, central goniometer table (grating/prism), and rotating telescope arm. |
| **4** | **3D Goniometer (شبیه‌ساز سه‌بعدی)** | Isometric 3D rendering of heavy cast-iron base, graduated circle, leveling screws, optical arms, and light dispersion. |
| **5** | **1D Spectral Profile (پروفایل شدت)** | Calibrated intensity vs. angle plot $I(\theta)$ displaying peaks, FWHM widths, and resolving limits. |
| **6** | **Calculations (کاربرگ محاسبات)** | Live mathematical card substitutions, Rydberg constant solver, Cauchy dispersion inversion, and recorded measurement data table. |
| **7** | **User Guide (راهنمای کاربری)** | In-app illustrated laboratory manual matching university optics experiment guidelines. |

---

## Interactive Controls & Shortcuts

- **Mouse Dragging on Eyepiece / 2D Canvas**: Click and drag horizontally to rotate the telescope arm.
- **Mouse Dragging on Vernier Loupes**: Click and drag on either loupe to rotate the circular graduated scale with mechanical ratchet sound effects.
- **Mouse Wheel**: Scroll wheel over Vernier loupes to micro-step by exactly $\pm 1'$ ($0.0167^\circ$).
- **Micro-Step Buttons**:
  - `[-1°]`, `[-10']`, `[◀ -1']` (Step counter-clockwise)
  - `[+1' ▶]`, `[+10']`, `[+1°]` (Step clockwise)
- **Locking Clamp**: Toggle coarse rotation lock to enable the fine micrometer tangent screw.
- **Fine Tangent Screw**: Precision adjustment range of $\pm 5.0^\circ$ around the clamped position.
- **Keyboard Shortcuts**:
  - `F11`: Toggle Fullscreen mode.
  - `Escape`: Exit Fullscreen mode.
  - `Ctrl + S`: Record current telescope angle to laboratory observation worksheet.
  - `Ctrl + P`: Export laboratory report to Word (`.docx`).

---

## Laboratory Report Generation

### Microsoft Word (`.docx`) with Native OMML Equations
The built-in exporter creates academic-grade Word documents containing:
- Complete experiment metadata, date, and apparatus parameters.
- Native Office Math Markup Language (`<m:oMath>`) equation blocks (editable in Word equation editor).
- Formatted observation tables with Vernier 1, Vernier 2, corrected angles, calculated wavelengths, and error percentages.
- Dedicated Hydrogen Balmer and Rydberg constant determination sections.

### CSV Dataset (UTF-8-SIG)
Exports all recorded measurement rows with UTF-8 Byte Order Mark (BOM) for direct opening in Microsoft Excel without character encoding corruption.

---

## Installation & Running

### Option A: Portable Windows Executable (Recommended)
No Python installation or dependencies required:
1. Go to the [Releases](https://github.com/AmirMoYousefVand/SpectroMeter-Simulator/releases) page.
2. Download `SpectroMeter_Simulator.exe`.
3. Double-click to launch.

### Option B: Running from Source
Requires Python 3.10 or higher:
```bash
# Clone the repository
git clone https://github.com/AmirMoYousefVand/SpectroMeter-Simulator.git
cd SpectroMeter-Simulator

# Install required dependencies
pip install -r requirements.txt

# Launch simulator
python main.py
```

### Running Test Suite
Execute the 12 automated verification test suites:
```bash
python test_spectrometer.py
```

---

## Building Standalone Executable

To compile a standalone portable `.exe` from source using PyInstaller:
```bash
pip install pyinstaller
python -m PyInstaller --clean spectrometer.spec
```
The output binary will be located at `dist/SpectroMeter_Simulator.exe`.

---

## Release History

### v1.1.0 (Fall 2026 / 1405)
- **Vector Icons**: Replaced all Unicode emojis with clean, open-source vector UI icons (moon, volume on/mute).
- **GitHub Footer**: Added direct repository link button with official GitHub icon in the main window footer.
- **Deduction Dialog**: Cleaned feedback formatting without emoji or glyph artifacts.
- **Typography**: Complete Vazirmatn and Space Grotesk font integration with native Windows Uniscribe shaping.
- **Standalone Windows Executable**: Bundled and published standalone `.exe` release.

### v1.0.0
- Initial public release with Fraunhofer diffraction, Cauchy prism dispersion, dual vernier reading, Balmer series Rydberg extraction, and OMML Word export.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
