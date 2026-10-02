@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo   MIDI-To-Strudel - Packaging Standalone Executable
echo ===================================================
echo.

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 'uv' was not found in PATH.
    echo Please run 'install.bat' first to install uv and dependencies.
    echo.
    pause
    exit /b 1
)

echo [1/2] Checking and syncing dependencies via uv...
uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to sync dependencies with uv.
    pause
    exit /b 1
)

echo.
echo [2/2] Compiling standalone executable with PyInstaller...
echo This may take 30-60 seconds...
echo.

uv run pyinstaller --noconsole --onefile --clean --name "MIDI-to-Strudel" --add-data "Midi-to-Strudel.py;." gui.py

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo   [SUCCESS] Standalone EXE compiled successfully!
    echo   Location: dist\MIDI-to-Strudel.exe
    echo ===================================================
    echo.
    echo Opening output folder...
    explorer "%~dp0dist"
) else (
    echo.
    echo [ERROR] PyInstaller build failed! Check the output messages above.
)

echo.
pause
