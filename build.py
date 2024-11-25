import PyInstaller.__main__
import os
import shutil

# Create dist directory if it doesn't exist
if not os.path.exists('dist'):
    os.makedirs('dist')

# Copy static files
if not os.path.exists('dist/static'):
    os.makedirs('dist/static')
shutil.copy2('static/fallback.svg', 'dist/static/')
shutil.copy2('favicon.ico', 'dist/static/')

# Create PyInstaller spec
PyInstaller.__main__.run([
    'findyourtab_native.py',
    '--name=FindYourTab',
    '--onefile',
    '--windowed',
    '--icon=favicon.ico',
    '--add-data=static;static',
])

# Create README.txt
readme_content = """FindYourTab Installation Guide

1. Install the browser extension:
   - Chrome/Brave: Visit chrome://extensions, enable Developer Mode, and load unpacked extension
   - Firefox: Visit about:debugging, click "This Firefox", and load temporary add-on

2. Run FindYourTab:
   - Double-click FindYourTab.exe
   - The app will start in your system tray
   - Use Ctrl+Alt+F to show/hide the window

3. Enjoy using FindYourTab!

Note: Keep FindYourTab running to use the extension.
"""

with open('dist/README.txt', 'w') as f:
    f.write(readme_content) 