# -*- mode: python ; coding: utf-8 -*-

# Add these two lines at the very top of your .spec file
from PyInstaller.utils.hooks import collect_data_files
block_cipher = None


a = Analysis(
    ['srteapp.py'],
    pathex=['C:\\Users\\OIE 21\\srte'], # Ensure your project root is here
    binaries=[],
    datas=[
        ('C:\\Users\\OIE 21\\srte\\srtemodules', 'srtemodules'), # Include your entire srtemodules folder
        ('C:\\Users\\OIE 21\\srte\\srtemodules\\DejaVuSans.ttf', '.'), # Include the font file
        ('C:\\Users\\OIE 21\\srte\\srtemodules\\DejaVuSans.json', '.'), # Include the font JSON
        # Add any other data files your app might need here, e.g., if you have images or other CSVs
        # ('path/to/your/other_data.csv', '.'),
    ],
    # Add 'streamlit' to hiddenimports to ensure its metadata is bundled
    hiddenimports=['streamlit'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SRTE_App',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_info_entries={
              '__pyinstaller_init_mode': 'immediate',
          },
          console=True,
          disable_windowed_traceback=False,
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
