# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['tray.py'],
    pathex=[],
    binaries=[],
    datas=[('icons', 'icons'), ('prayer_data.json', '.')],
    hiddenimports=['PIL._tkinter_finder', 'pystray._win32', 'prayer_calculator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EMSTEEL_Prayer_Agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Emsteel2026.ico'],
)
