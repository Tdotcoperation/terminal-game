#!/bin/bash
cd "$(dirname "$0")/.."
if command -v python3 >/dev/null 2>&1; then
  exec python3 terminal_arcade.py
fi
echo "Python 3 is required to run Terminal Arcade."
echo "Install Python 3 and run this file again."
read -r -p "Press Enter to close..."
