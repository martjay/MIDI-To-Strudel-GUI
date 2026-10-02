#!/usr/bin/env bash
# ==============================================================================
# MIDI-To-Strudel - Standalone macOS App Bundle (.app) Builder
# Uses PyInstaller and uv to compile a native macOS Application bundle.
# ==============================================================================

set -e

# Change directory to the script's root folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

echo "==================================================="
echo "  MIDI-To-Strudel - Packaging macOS Application (.app)"
echo "==================================================="
echo ""

if ! command -v uv >/dev/null 2>&1; then
    echo "[ERROR] 'uv' was not found in PATH."
    echo "Please run './install.sh' first to install uv and dependencies."
    exit 1
fi

echo "[1/2] Checking and syncing dependencies via uv..."
uv sync

echo ""
echo "[2/2] Compiling native macOS Application bundle (.app) with PyInstaller..."
echo "This may take 30-60 seconds..."
echo ""

# On macOS / Unix, PyInstaller --add-data uses a colon ':' separator
uv run pyinstaller \
    --noconsole \
    --windowed \
    --clean \
    --name "MIDI-to-Strudel" \
    --add-data "Midi-to-Strudel.py:." \
    gui.py

if [ -d "dist/MIDI-to-Strudel.app" ] || [ -f "dist/MIDI-to-Strudel" ]; then
    echo ""
    echo "==================================================="
    echo "  [SUCCESS] macOS Application built successfully!"
    echo "  Location: dist/MIDI-to-Strudel.app"
    echo "==================================================="
    echo ""
    if command -v open >/dev/null 2>&1; then
        echo "Opening dist folder in Finder..."
        open "$SCRIPT_DIR/dist"
    fi
else
    echo "[ERROR] Build failed! Check the output messages above."
    exit 1
fi
