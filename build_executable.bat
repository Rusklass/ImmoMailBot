@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
pyinstaller --onefile --name ImmoBot --icon=NONE main.py

echo.
echo Build complete!
echo Your executable is in the "dist" folder.
pause
