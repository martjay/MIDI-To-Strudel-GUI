#!/usr/bin/env bash
# ==============================================================================
# MIDI-To-Strudel - One-Click Installer for macOS
# Automatically checks/installs 'uv' and syncs all project dependencies.
# ==============================================================================

set -e

# Change directory to the script's root folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================================="
echo "  MIDI-To-Strudel - macOS Environment Setup"
echo "==================================================="
echo ""

# Ensure user local bin paths are in PATH
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# Check if 'uv' package manager is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "[1/2] 'uv' was not found on your system."
    echo "      Installing Astral 'uv' via official installer..."
    echo ""
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv >/dev/null 2>&1; then
        echo "[ERROR] Failed to install 'uv'. Please install manually: brew install uv"
        exit 1
    fi
    echo "      [OK] 'uv' installed successfully!"
else
    echo "[1/2] [OK] 'uv' package manager detected: $(uv --version)"
fi

echo ""
echo "[2/2] Installing dependencies and syncing virtual environment via uv..."
uv sync

echo ""
echo "==================================================="
echo "  [SUCCESS] All dependencies installed successfully!"
echo "==================================================="
echo ""
echo "You can now run:"
echo "  ./run.sh          - Launch the Drag-and-Drop GUI app"
echo "  ./build_macos.sh  - Build standalone macOS .app bundle"
echo ""
