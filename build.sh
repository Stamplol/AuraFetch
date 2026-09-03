#!/bin/bash
set -e
echo "Building AuraFetch..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
if [ -f "AuraFetch.spec" ]; then
  pyinstaller --noconfirm --clean AuraFetch.spec
else
  pyinstaller --noconfirm --clean --onefile --windowed --name AuraFetch --collect-all customtkinter app.py
fi
echo ""
echo "Done. Binary at dist/AuraFetch"
ls -lh dist/AuraFetch 2>/dev/null || ls -lh dist/ | head -20
