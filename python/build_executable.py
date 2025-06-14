#!/usr/bin/env python3
"""
Build script for FindYourTab executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['findyourtab_native.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),
    ],
    hiddenimports=[
        'webview',
        'websockets',
        'psutil',
        'keyboard',
        'asyncio',
        'json',
        'threading',
        'ctypes',
        'logging'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='FindYourTab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('FindYourTab.spec', 'w') as f:
        f.write(spec_content.strip())
    print("✓ Spec file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Build using spec file
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "FindYourTab.spec"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Executable built successfully!")
        print(f"✓ Location: {os.path.abspath('dist/FindYourTab.exe')}")
        return True
    else:
        print("✗ Build failed:")
        print(result.stderr)
        return False

def create_installer_files():
    """Create additional files for distribution"""
    
    # Create README for the executable
    readme_content = """# FindYourTab - Desktop Application

## Quick Start
1. Run `FindYourTab.exe`
2. Install the browser extension from the Chrome Web Store
3. Use Ctrl+Alt+F to toggle the tab finder window

## Features
- View all browser tabs in one place
- Instant tab switching
- Cross-browser support
- Keyboard shortcuts
- System tray integration

## System Requirements
- Windows 10/11
- Chrome, Firefox, Edge, or Opera browser
- 4GB RAM minimum

## Troubleshooting
- If the app doesn't start, run as administrator
- Make sure Windows Defender isn't blocking the executable
- Check that port 8765 and 8000 are available

## Support
Visit: https://github.com/yourusername/findyourtab
"""
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    
    # Create version info
    version_info = """FindYourTab v1.0.0
Built: {date}
Platform: Windows x64
Python: {python_version}
""".format(
        date=subprocess.check_output(['date', '/t'], shell=True, text=True).strip(),
        python_version=sys.version.split()[0]
    )
    
    with open('dist/version.txt', 'w') as f:
        f.write(version_info)
    
    print("✓ Distribution files created")

def main():
    """Main build process"""
    print("🚀 Building FindYourTab Executable")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('findyourtab_native.py'):
        print("✗ Error: findyourtab_native.py not found!")
        print("Please run this script from the python/ directory")
        return False
    
    try:
        install_pyinstaller()
        create_spec_file()
        
        if build_executable():
            create_installer_files()
            print("\n🎉 Build completed successfully!")
            print(f"📁 Executable location: {os.path.abspath('dist/FindYourTab.exe')}")
            print(f"📦 File size: {os.path.getsize('dist/FindYourTab.exe') / 1024 / 1024:.1f} MB")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"✗ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 