@echo off
echo Building AuraFetch.exe ...
python -m pip install --upgrade pip
pip install -r requirements.txt
if exist AuraFetch.spec (
  pyinstaller --noconfirm --clean AuraFetch.spec
) else (
  pyinstaller --noconfirm --clean --onefile --windowed --name AuraFetch --collect-all customtkinter app.py
)
echo.
echo Done. Check dist\AuraFetch.exe
if exist dist\AuraFetch.exe (
  echo Size:
  for %%A in (dist\AuraFetch.exe) do echo %%~zA bytes
)
pause
