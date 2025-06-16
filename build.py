"""
MIT License

Copyright (c) 2025 whybirdslie (FindYourTab)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Any modifications or contributions to this software must maintain attribution to the original author (whybirdslie) and share credit for the work.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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