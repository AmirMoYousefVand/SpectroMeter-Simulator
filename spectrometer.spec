# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

ctk_datas = collect_data_files('customtkinter')
docx_datas = collect_data_files('docx')

project_datas = [
    ('assets', 'assets'),
] + ctk_datas + docx_datas

hidden_imports = [
    'PIL._tkinter_finder',
    'matplotlib.backends.backend_tkagg',
    'scipy',
    'scipy.signal',
    'arabic_reshaper',
    'bidi.algorithm',
    'docx',
    'customtkinter',
] + collect_submodules('customtkinter')

# Exclude unrelated heavy frameworks installed in global Python environment
excludes = [
    'paddle',
    'paddleocr',
    'torch',
    'torchvision',
    'torchaudio',
    'cv2',
    'opencv',
    'tensorflow',
    'tensorboard',
    'keras',
    'llvmlite',
    'numba',
    'triton',
    'cuda',
    'caffe',
    'IPython',
    'notebook',
    'pytest',
    'unittest',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=project_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpectroMeter_Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.abspath('assets/Logo/favicon.ico'),
)
