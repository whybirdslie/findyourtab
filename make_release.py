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

import os
import shutil
import zipfile

def make_release():
    # Run PyInstaller build
    os.system('python build.py')
    
    # Create release directory
    if not os.path.exists('release'):
        os.makedirs('release')

    # Create Chrome/Brave extension zip
    with zipfile.ZipFile('release/findyourtab_chrome.zip', 'w') as zf:
        for root, dirs, files in os.walk('extension/build'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'extension/build')
                zf.write(file_path, arcname)

    # Create Firefox extension zip
    with zipfile.ZipFile('release/findyourtab_firefox.zip', 'w') as zf:
        for root, dirs, files in os.walk('firefox-build/public'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'firefox-build/public')
                zf.write(file_path, arcname)

    # Create application zip
    with zipfile.ZipFile('release/findyourtab_app.zip', 'w') as zf:
        for file in os.listdir('dist'):
            file_path = os.path.join('dist', file)
            if os.path.isfile(file_path):
                zf.write(file_path, file)
            elif os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for f in files:
                        full_path = os.path.join(root, f)
                        arcname = os.path.relpath(full_path, 'dist')
                        zf.write(full_path, arcname)

if __name__ == '__main__':
    make_release() 