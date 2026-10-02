@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo   MIDI-To-Strudel - Environment Setup with uv
echo ===================================================
echo.

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 'uv' package manager was not found in your PATH.
    echo.
    echo To install uv on Windows, run the following in PowerShell:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Or install via pip:
    echo   pip install uv
    echo.
    pause
    exit /b 1
)

echo [INFO] Found uv package manager.
echo [INFO] Creating virtual environment and syncing dependencies...
echo.

uv sync

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo   [SUCCESS] All dependencies installed successfully!
    echo   - Launch GUI:     run.bat
    echo   - Build .exe:     build_exe.bat
    echo ===================================================
) else (
    echo.
    echo [ERROR] uv sync failed. Please check the logs above.
)

echo.
pause
