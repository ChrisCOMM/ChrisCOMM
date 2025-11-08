#!/bin/bash
# NFIRS Data Extraction and Analysis Script
# Usage: ./extract_and_analyze.sh <path_to_zip_file>

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "============================================"
echo "NFIRS Solar Panel & Battery Fire Analysis"
echo "============================================"
echo ""

# Check if zip file path provided
if [ -z "$1" ]; then
    # Check for zip files in current directory
    ZIP_FILES=(*.zip)
    if [ -e "${ZIP_FILES[0]}" ]; then
        ZIP_FILE="${ZIP_FILES[0]}"
        echo "📦 Found zip file: $ZIP_FILE"
    else
        echo "❌ No zip file found!"
        echo ""
        echo "Usage: ./extract_and_analyze.sh <path_to_zip_file>"
        echo ""
        echo "Or copy your NFIRS zip file to this directory and run again:"
        echo "  cp /path/to/nfirs_data.zip ."
        echo "  ./extract_and_analyze.sh"
        exit 1
    fi
else
    ZIP_FILE="$1"
    if [ ! -f "$ZIP_FILE" ]; then
        echo "❌ Error: File not found: $ZIP_FILE"
        exit 1
    fi
fi

echo ""
echo "Step 1: Extracting NFIRS data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create data directory if it doesn't exist
mkdir -p data

# Extract zip file
unzip -o -q "$ZIP_FILE" -d data/

echo "✓ Data extracted to data/"
echo ""

# List extracted files
echo "📋 Extracted files:"
ls -lh data/*.{csv,CSV,txt,TXT} 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# Convert uppercase filenames to lowercase
echo "Step 2: Standardizing file names..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd data
for file in *.CSV *.TXT 2>/dev/null; do
    if [ -f "$file" ]; then
        lowercase=$(echo "$file" | tr '[:upper:]' '[:lower:]')
        if [ "$file" != "$lowercase" ]; then
            mv "$file" "$lowercase"
            echo "  Renamed: $file → $lowercase"
        fi
    fi
done
cd ..
echo "✓ File names standardized"
echo ""

# Check for required files
echo "Step 3: Verifying NFIRS modules..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BASIC_FILE=""
FIRE_FILE=""

# Look for basic incident file
for name in basicincident basic_incident basicinc; do
    if [ -f "data/${name}.csv" ]; then
        BASIC_FILE="data/${name}.csv"
        echo "  ✓ Basic module: ${name}.csv"
        break
    fi
done

# Look for fire incident file
for name in fireincident fire_incident fireinc; do
    if [ -f "data/${name}.csv" ]; then
        FIRE_FILE="data/${name}.csv"
        echo "  ✓ Fire module: ${name}.csv"
        break
    fi
done

if [ -f "data/structurefire.csv" ]; then
    echo "  ✓ Structure module: structurefire.csv"
fi

echo ""

if [ -z "$BASIC_FILE" ]; then
    echo "⚠️  Warning: Basic incident module not found"
    echo "    Looking for files matching: basicincident.csv, basic_incident.csv"
    echo ""
    echo "    Available CSV files:"
    ls -1 data/*.csv 2>/dev/null | sed 's/^/      /'
    echo ""
fi

# Get data statistics
if [ -n "$BASIC_FILE" ]; then
    echo "Step 4: Analyzing data statistics..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python src/main.py stats --input "$BASIC_FILE" || echo "⚠️  Could not read data file"
    echo ""
fi

# Run analysis
echo "Step 5: Running solar panel & battery fire analysis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/main.py analyze --type all --year 2024 --format all

echo ""
echo "============================================"
echo "✅ Analysis Complete!"
echo "============================================"
echo ""
echo "📊 Reports available in:"
LATEST_REPORT=$(ls -td reports/*/ 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo "  $LATEST_REPORT"
    echo ""
    echo "  📄 Files:"
    ls -lh "$LATEST_REPORT"* 2>/dev/null | awk '{print "    • " $9 " (" $5 ")"}'
fi
echo ""
