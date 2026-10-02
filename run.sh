#!/usr/bin/env bash
# ==============================================================================
# MIDI-To-Strudel - One-Click Launcher for macOS
# Starts the PyQt6 Drag-and-Drop GUI interface.
# ==============================================================================

set -e

# Change directory to the script's root folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
    echo "[ERROR] 'uv' was not found in PATH."
    echo "Please run './install.sh' first to install uv and dependencies."
    exit 1
fi

echo "Starting MIDI to Strudel GUI on macOS..."
uv run python gui.py "$@"
