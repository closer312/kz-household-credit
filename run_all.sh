#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/src"
python3 01_build_panel.py
python3 02_descriptives.py
python3 03_figures.py
python3 04_presentation.py
