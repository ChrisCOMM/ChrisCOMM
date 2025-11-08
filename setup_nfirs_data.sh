#!/bin/bash
# NFIRS Data Setup Helper Script

echo "=== NFIRS Data Setup Helper ==="
echo ""

# Check if zip file path is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup_nfirs_data.sh /path/to/nfirs_data.zip"
    echo ""
    echo "Or manually:"
    echo "1. Place your zip file in the project directory"
    echo "2. Run: unzip your_file.zip -d data/"
    echo ""
    exit 1
fi

ZIP_FILE="$1"

if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ Error: File not found: $ZIP_FILE"
    exit 1
fi

echo "📦 Extracting NFIRS data..."
unzip -q "$ZIP_FILE" -d data/

echo "✓ Data extracted to data/"
echo ""

echo "📋 Files found:"
ls -lh data/*.csv data/*.txt 2>/dev/null || echo "No CSV files found in data/"
echo ""

echo "🔍 Looking for NFIRS module files..."
if [ -f data/basicincident.csv ] || [ -f data/BASICINCIDENT.csv ]; then
    echo "  ✓ Basic module found"
fi

if [ -f data/fireincident.csv ] || [ -f data/FIREINCIDENT.csv ]; then
    echo "  ✓ Fire module found"
fi

if [ -f data/structurefire.csv ] || [ -f data/STRUCTUREFIRE.csv ]; then
    echo "  ✓ Structure fire module found"
fi

echo ""
echo "📊 To analyze your data, run:"
echo "  python src/main.py stats --input data/basicincident.csv"
echo "  python src/main.py analyze --type all"
echo ""
