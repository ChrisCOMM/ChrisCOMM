@echo off
REM Windows Batch Script to Analyze NFIRS Data
REM Place this file in your ChrisCOMM directory

echo ============================================
echo NFIRS Solar Panel and Battery Fire Analysis
echo ============================================
echo.

set ZIP_FILE=C:\Users\EU01242390\Downloads\nfirs_all_incident_pdr_2024.zip

if not exist "%ZIP_FILE%" (
    echo Error: File not found: %ZIP_FILE%
    echo.
    echo Please update the ZIP_FILE path in this script.
    pause
    exit /b 1
)

echo Step 1: Extracting NFIRS data...
echo ----------------------------------------
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath 'data' -Force"
echo Done!
echo.

echo Step 2: Checking extracted files...
echo ----------------------------------------
dir data\*.csv
echo.

echo Step 3: Installing dependencies (if needed)...
echo ----------------------------------------
pip install -q pandas pyyaml click numpy
echo.

echo Step 4: Running analysis...
echo ----------------------------------------
python src\main.py analyze --type all --year 2024 --format all
echo.

echo ============================================
echo Analysis Complete!
echo ============================================
echo.
echo Reports are available in the reports\ directory
dir /s reports\*.html
echo.
pause
