"""
Interactive 3D Apparatus Setup View (نمای سه‌بعدی دستگاه اسپکترومتر).
Renders the complete physical spectrometer in 3D using Matplotlib 3D:
- Heavy cast iron base and central vertical column
- Circular graduated protractor table
- Fixed Collimator cylinder and adjustable entrance slit box
- Rotating Telescope tube, objective cell, and eyepiece assembly
- Central Prism/Grating stage with 3 leveling thumbscrews
- 3D diffracted optical ray tubes radiating at theoretical angles
- Smooth camera controls: mouse wheel zoom, manual rotation buttons, and preset angles.
"""

from typing import List, Optional, Tuple
import customtkinter as ctk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from physics.spectrometer_model import SpectrometerModel
from physics.grating_engine import DiffractedPeak
from physics.constants import SpectralSource
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService
from utils.font_manager import FontManager

class Apparatus3DView(ctk.CTkFrame):
    """
    Embeds interactive 3D laboratory scene with rotatable and zoomable 3D projection.
    """

    def __init__(self, master, model: SpectrometerModel, **kwargs):
        super().__init__(master, **kwargs)
        self.model = model
        self.optic_mode = "grating" # "grating" or "prism"

        # Camera tracking
        self.zoom_level = 1.0
        self.default_elev = 26.0
        self.default_azim = -50.0

        # Base 3D bounding limits
        self.base_xlim = (-0.35, 0.35)
        self.base_ylim = (-0.35, 0.35)
        self.base_zlim = (-0.25, 0.35)

        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)
        font_num = FontManager.get_number_font(10)

        # ----------------------------------------------------------------------
        # 1. Top Camera Angle & Navigation Control Toolbar
        # ----------------------------------------------------------------------
        toolbar = ctk.CTkFrame(self, fg_color="#18181F", corner_radius=8, height=36)
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 2))

        # Camera Presets (Clean standard strings for CTkLabel/CTkButton)
        self.lbl_cam = ctk.CTkLabel(toolbar, text=LocalizationService.t("cam_label"), font=font_btn)
        self.lbl_cam.pack(side="left", padx=(8, 4))

        self.btn_cam_persp = ctk.CTkButton(toolbar, text=LocalizationService.t("cam_perspective"), width=68, height=22, font=font_btn, command=self._set_cam_perspective)
        self.btn_cam_persp.pack(side="left", padx=1)

        self.btn_cam_top = ctk.CTkButton(toolbar, text=LocalizationService.t("cam_top"), width=52, height=22, font=font_btn, command=self._set_cam_top)
        self.btn_cam_top.pack(side="left", padx=1)

        self.btn_cam_eye = ctk.CTkButton(toolbar, text=LocalizationService.t("cam_eyepiece"), width=68, height=22, font=font_btn, command=self._set_cam_eyepiece)
        self.btn_cam_eye.pack(side="left", padx=1)

        self.btn_cam_front = ctk.CTkButton(toolbar, text=LocalizationService.t("cam_front"), width=48, height=22, font=font_btn, command=self._set_cam_front)
        self.btn_cam_front.pack(side="left", padx=1)

        # Rotation Controls
        self.lbl_rot = ctk.CTkLabel(toolbar, text=LocalizationService.t("rot_label"), font=font_btn)
        self.lbl_rot.pack(side="left", padx=(8, 2))

        ctk.CTkButton(toolbar, text="◀", width=22, height=22, font=font_num, command=lambda: self._rotate_camera(azim_delta=-10)).pack(side="left", padx=1)
        ctk.CTkButton(toolbar, text="▶", width=22, height=22, font=font_num, command=lambda: self._rotate_camera(azim_delta=10)).pack(side="left", padx=1)
        ctk.CTkButton(toolbar, text="▲", width=22, height=22, font=font_num, command=lambda: self._rotate_camera(elev_delta=6)).pack(side="left", padx=1)
        ctk.CTkButton(toolbar, text="▼", width=22, height=22, font=font_num, command=lambda: self._rotate_camera(elev_delta=-6)).pack(side="left", padx=1)

        # Zoom Controls
        ctk.CTkButton(toolbar, text="+", width=22, height=22, font=font_num, command=lambda: self._apply_zoom_factor(1.15)).pack(side="left", padx=(6, 1))
        ctk.CTkButton(toolbar, text="-", width=22, height=22, font=font_num, command=lambda: self._apply_zoom_factor(1.0 / 1.15)).pack(side="left", padx=1)

        # Telemetry badge
        self.telemetry_label = ctk.CTkLabel(
            toolbar,
            text="Elev: 26° | Azim: -50° | Zoom: 1.0x",
            font=font_num,
            text_color="#94A3B8"
        )
        self.telemetry_label.pack(side="right", padx=8)

        # ----------------------------------------------------------------------
        # 2. Matplotlib 3D Canvas
        # ----------------------------------------------------------------------
        self.fig = Figure(figsize=(7, 4.4), dpi=100, facecolor="#101014")
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_facecolor("#101014")

        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor("#26262E")
        self.ax.yaxis.pane.set_edgecolor("#26262E")
        self.ax.zaxis.pane.set_edgecolor("#26262E")
        self.ax.grid(True, linestyle=":", alpha=0.25, color="#52525B")
        self.ax.tick_params(colors="#71717A", labelsize=7)

        self.ax.view_init(elev=self.default_elev, azim=self.default_azim)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky="nsew", padx=8, pady=(2, 6))

        # Mouse scroll zoom binding
        self.canvas.mpl_connect("scroll_event", self._on_scroll_zoom)

    def refresh_language(self):
        """Updates toolbar button texts for current language."""
        is_fa = LocalizationService.is_persian()
        font_btn = FontManager.get_ui_font(11, "bold", is_fa)

        self.lbl_cam.configure(text=LocalizationService.t("cam_label"), font=font_btn)
        self.btn_cam_persp.configure(text=LocalizationService.t("cam_perspective"), font=font_btn)
        self.btn_cam_top.configure(text=LocalizationService.t("cam_top"), font=font_btn)
        self.btn_cam_eye.configure(text=LocalizationService.t("cam_eyepiece"), font=font_btn)
        self.btn_cam_front.configure(text=LocalizationService.t("cam_front"), font=font_btn)
        self.lbl_rot.configure(text=LocalizationService.t("rot_label"), font=font_btn)

    def _on_scroll_zoom(self, event):
        if event.inaxes != self.ax:
            return
        step = getattr(event, "step", 0)
        btn = getattr(event, "button", None)
        if btn == "up" or step > 0:
            self._apply_zoom_factor(1.15)
        elif btn == "down" or step < 0:
            self._apply_zoom_factor(1.0 / 1.15)

    def _apply_zoom_factor(self, factor: float):
        new_zoom = self.zoom_level * factor
        if not (0.35 <= new_zoom <= 5.0):
            return
        self.zoom_level = new_zoom

        scale = 1.0 / self.zoom_level
        self.ax.set_xlim([x * scale for x in self.base_xlim])
        self.ax.set_ylim([y * scale for y in self.base_ylim])
        self.ax.set_zlim([z * scale for z in self.base_zlim])

        self._update_telemetry()
        self.canvas.draw()

    def _rotate_camera(self, azim_delta: float = 0, elev_delta: float = 0):
        azim = (self.ax.azim + azim_delta) % 360
        elev = np.clip(self.ax.elev + elev_delta, -89.0, 89.0)
        self.ax.view_init(elev=elev, azim=azim)
        self._update_telemetry()
        self.canvas.draw()

    def _update_telemetry(self):
        elev = self.ax.elev
        azim = self.ax.azim
        self.telemetry_label.configure(
            text=f"Elev: {elev:.0f}° | Azim: {azim:.0f}° | Zoom: {self.zoom_level:.1f}x"
        )

    # Preset Camera Positions
    def _set_cam_perspective(self):
        self.ax.view_init(elev=26, azim=-50)
        self._update_telemetry()
        self.canvas.draw()

    def _set_cam_top(self):
        self.ax.view_init(elev=89, azim=-90)
        self._update_telemetry()
        self.canvas.draw()

    def _set_cam_eyepiece(self):
        tele_ang = self.model.effective_telescope_angle
        self.ax.view_init(elev=10, azim=tele_ang + 180)
        self._update_telemetry()
        self.canvas.draw()

    def _set_cam_front(self):
        self.ax.view_init(elev=8, azim=0)
        self._update_telemetry()
        self.canvas.draw()

    # ==========================================================================
    # 3D Scene Geometry Reconstruction
    # ==========================================================================
    def render_3d_apparatus(
        self,
        peaks: Optional[List[DiffractedPeak]] = None,
        source: Optional[SpectralSource] = None
    ):
        """Builds 3D meshes for spectrometer stand, collimator, telescope, table, and rays."""
        curr_elev = self.ax.elev if hasattr(self.ax, "elev") else self.default_elev
        curr_azim = self.ax.azim if hasattr(self.ax, "azim") else self.default_azim

        self.ax.cla()
        self.ax.set_facecolor("#101014")
        self.ax.grid(True, linestyle=":", alpha=0.25, color="#52525B")
        self.ax.tick_params(colors="#71717A", labelsize=7)

        self.ax.set_xlabel("X (m)", color="#A1A1AA", fontsize=8, labelpad=2)
        self.ax.set_ylabel("Y (m)", color="#A1A1AA", fontsize=8, labelpad=2)
        self.ax.set_zlabel("Z (m)", color="#A1A1AA", fontsize=8, labelpad=2)

        # Apply limits with zoom
        scale = 1.0 / self.zoom_level
        self.ax.set_xlim([x * scale for x in self.base_xlim])
        self.ax.set_ylim([y * scale for y in self.base_ylim])
        self.ax.set_zlim([z * scale for z in self.base_zlim])

        # ----------------------------------------------------------------------
        # 1. Cast-Iron Tripod Base & Center Column
        # ----------------------------------------------------------------------
        z_base = -0.18
        theta_base = np.linspace(0, 2*np.pi, 24)
        r_base = 0.16
        # Base disk
        x_base = r_base * np.cos(theta_base)
        y_base = r_base * np.sin(theta_base)
        self.ax.plot(x_base, y_base, [z_base]*24, color="#3F3F46", lw=3)

        # Vertical Column (Chrome cylinder from base to scale table)
        z_col = np.linspace(z_base, 0.0, 10)
        self.ax.plot([0]*10, [0]*10, z_col, color="#E2E8F0", lw=7)

        # Circular Protractor Disk (z = 0.0)
        r_disk = 0.14
        x_disk = r_disk * np.cos(theta_base)
        y_disk = r_disk * np.sin(theta_base)
        self.ax.plot(x_disk, y_disk, [0.0]*24, color="#F59E0B", lw=2)

        # ----------------------------------------------------------------------
        # 2. Fixed Collimator Arm (at Y = 0, extending along -X axis)
        # ----------------------------------------------------------------------
        x_coll = np.linspace(-0.25, -0.04, 15)
        self.ax.plot(x_coll, [0]*15, [0.04]*15, color="#D97706", lw=8) # Brass tube
        # Slit Box on far left
        self.ax.scatter([-0.25], [0], [0.04], color="#EF4444", s=140, marker="s")
        # Objective lens cell near center
        self.ax.scatter([-0.04], [0], [0.04], color="#0284C7", s=110, marker="o")

        # ----------------------------------------------------------------------
        # 3. Central Stage with 3 Thumbscrews & Glass Grating Plate
        # ----------------------------------------------------------------------
        z_table = 0.02
        r_stage = 0.05
        x_stage = r_stage * np.cos(theta_base)
        y_stage = r_stage * np.sin(theta_base)
        self.ax.plot(x_stage, y_stage, [z_table]*24, color="#71717A", lw=2)

        if self.optic_mode == "prism":
            # 3D Equilateral Glass Prism
            side = 0.04
            h_prism = 0.05
            p1 = np.array([-side/2, -side*0.288, z_table])
            p2 = np.array([side/2, -side*0.288, z_table])
            p3 = np.array([0, side*0.577, z_table])
            p1_top = np.array([-side/2, -side*0.288, z_table + h_prism])
            p2_top = np.array([side/2, -side*0.288, z_table + h_prism])
            p3_top = np.array([0, side*0.577, z_table + h_prism])

            prism_faces = [
                [p1, p2, p3],             # Bottom
                [p1_top, p2_top, p3_top], # Top
                [p1, p2, p2_top, p1_top], # Face 1
                [p2, p3, p3_top, p2_top], # Face 2
                [p3, p1, p1_top, p3_top], # Face 3
            ]
            prism_poly = Poly3DCollection(prism_faces, alpha=0.6, facecolor="#38BDF8", edgecolor="#BAE6FD", lw=1.2)
            self.ax.add_collection3d(prism_poly)
        else:
            # Transmission Grating Plate (Translucent Cyan Plate)
            gx = np.array([0, 0, 0, 0])
            gy = np.array([-0.025, 0.025, 0.025, -0.025])
            gz = np.array([z_table, z_table, z_table + 0.05, z_table + 0.05])
            verts = [list(zip(gx, gy, gz))]
            grating_poly = Poly3DCollection(verts, alpha=0.65, facecolor="#06B6D4", edgecolor="#A5F3FC", lw=1.5)
            self.ax.add_collection3d(grating_poly)

        # ----------------------------------------------------------------------
        # 4. Rotating Telescope Arm
        # ----------------------------------------------------------------------
        tele_ang = self.model.effective_telescope_angle
        tele_rad = np.radians(tele_ang)
        r_tele = np.linspace(0.04, 0.25, 15)
        x_tele = r_tele * np.cos(tele_rad)
        y_tele = r_tele * np.sin(tele_rad)
        z_tele = np.full(15, 0.04)

        # Telescope tube
        self.ax.plot(x_tele, y_tele, z_tele, color="#475569", lw=8)
        # Eyepiece cone at outer end
        self.ax.scatter([x_tele[-1]], [y_tele[-1]], [z_tele[-1]], color="#38BDF8", s=130, marker="^")
        # Objective cell facing grating
        self.ax.scatter([x_tele[0]], [y_tele[0]], [z_tele[0]], color="#0284C7", s=100, marker="o")

        # ----------------------------------------------------------------------
        # 5. 3D Optical Diffracted Rays
        # ----------------------------------------------------------------------
        # Incoming collimated beam (from -X to center)
        self.ax.plot([-0.25, 0], [0, 0], [0.04, 0.04], color="#FEF08A", lw=2, linestyle="--")

        # Diffracted beams radiating outward
        if peaks:
            for p in peaks:
                if p.is_missing_order or p.intensity <= 0:
                    continue
                p_rad = np.radians(p.angle_deg)
                ray_r = 0.22
                rx = ray_r * np.cos(p_rad)
                ry = ray_r * np.sin(p_rad)
                r_hex = ColorUtils.wavelength_to_hex(p.wavelength_nm) if not p.color_hint else p.color_hint
                lw = 2.5 if p.order_m == 0 else max(1.0, p.intensity * 2.0)
                self.ax.plot([0, rx], [0, ry], [0.04, 0.04], color=r_hex, lw=lw, alpha=0.85)

        self.ax.view_init(elev=curr_elev, azim=curr_azim)
        self.canvas.draw()
