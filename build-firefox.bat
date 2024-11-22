@echo off
echo Building Firefox extension...

:: Create build directory
if exist firefox-build rmdir /S /Q firefox-build
mkdir firefox-build
mkdir firefox-build\public
echo Created build directory

:: Copy necessary files
copy extension\public\manifest-firefox.json firefox-build\public\manifest.json
copy extension\public\chrome-polyfill.js firefox-build\public\
copy extension\public\background.js firefox-build\public\
copy extension\public\popup.html firefox-build\public\
copy extension\build\static\js\*.js firefox-build\public\index.js
copy extension\build\static\css\*.css firefox-build\public\index.css
echo Copied extension files

:: Create zip file using PowerShell
cd firefox-build\public
powershell -command "Compress-Archive -Path * -DestinationPath '..\..\findyourtab-firefox.zip' -Force"
cd ..\..
echo Created Firefox extension zip

echo Build complete! You can now load findyourtab-firefox.zip in Firefox
pause 