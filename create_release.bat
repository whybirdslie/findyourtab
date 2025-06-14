@echo off
echo 🚀 FindYourTab Release Creator
echo ================================

set /p version="Enter version (e.g., v1.0.0): "

echo.
echo Building executable...
cd python
python build_executable.py

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

cd ..

echo.
echo 📝 Creating git tag and pushing...
git add .
git commit -m "Release %version%: Updated executable and documentation"
git tag %version%
git push origin main
git push origin %version%

echo.
echo ✅ Release %version% created!
echo.
echo 📋 Next steps:
echo 1. GitHub Actions will automatically build and create the release
echo 2. Check: https://github.com/whybirdslie/findyourtab/releases
echo 3. The download link will be: https://github.com/whybirdslie/findyourtab/releases/latest/download/FindYourTab-Windows.zip
echo.
pause 