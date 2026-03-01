#!/usr/bin/env bash
set -euo pipefail

pyinstaller --noconfirm --onefile --windowed --name JuntarPDFs app_gui.py

echo "Executável gerado em dist/JuntarPDFs (ou .exe no Windows)."
