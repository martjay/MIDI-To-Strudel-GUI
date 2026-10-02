@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 'uv' was not found in PATH. Falling back to system Python...
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        start "" python gui.py %*
        exit /b 0
    ) else (
        echo [ERROR] Neither 'uv' nor 'python' was found in your PATH.
        echo Please run 'install.bat' first.
        pause
        exit /b 1
    )
)

start "" uv run python gui.py %*
exit /b 0
