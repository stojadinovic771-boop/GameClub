@echo off
setlocal
rem Always work from the folder this file is in (so double-clicking works too)
cd /d "%~dp0"

echo ==========================================
echo  GameClub - Installer Builder
echo ==========================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo Install from https://python.org - tick "Add Python to PATH"
    goto :end
)

echo.
echo Step 2: Installing packages (requirements.txt + PyInstaller)...
python -m pip install --upgrade pyinstaller -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    goto :end
)

echo.
echo Step 3: Checking icon...
if not exist "gameclub.ico" (
    echo ERROR: gameclub.ico not found.
    echo Put gameclub.ico in the same folder as BUILD.bat: %CD%
    goto :end
)
if not exist assets mkdir assets
copy /y "gameclub.ico" "assets\gameclub.ico" >nul

echo.
echo Step 4: Running PyInstaller...
if exist "dist\GameClub" rd /s /q "dist\GameClub"
if exist "build" rd /s /q "build"

python -m PyInstaller --name "GameClub" --onedir --windowed ^
    --icon "assets\gameclub.ico" ^
    --add-data "assets\gameclub.ico;assets" ^
    --hidden-import pygame --hidden-import PIL --collect-all pygame ^
    --hidden-import hid ^
    --collect-all winrt ^
    --uac-admin ^
    --noconfirm gameclub.py
if errorlevel 1 (
    echo ERROR: PyInstaller failed.
    goto :end
)

echo.
echo Step 5: Looking for NSIS...
set MAKENSIS=
if exist "C:\Program Files (x86)\NSIS\makensis.exe" set MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe
if exist "C:\Program Files\NSIS\makensis.exe" set MAKENSIS=C:\Program Files\NSIS\makensis.exe

if "%MAKENSIS%"=="" (
    echo NSIS not found.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo Then run this script again.
    goto :end
)

echo Found NSIS at: %MAKENSIS%

echo.
echo Step 6: Building installer...
if not exist "installer\gameclub.nsi" (
    echo ERROR: installer\gameclub.nsi not found.
    goto :end
)
"%MAKENSIS%" installer\gameclub.nsi
if errorlevel 1 (
    echo ERROR: NSIS build failed.
    goto :end
)

echo.
echo ==========================================
echo  SUCCESS! GameClub_Setup.exe is ready.
echo  Location: %CD%\GameClub_Setup.exe
echo ==========================================

:end
echo.
pause
