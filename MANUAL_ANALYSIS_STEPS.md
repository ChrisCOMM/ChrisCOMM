# Manual Analysis Steps for Your NFIRS Data

## Your File
`C:\Users\EU01242390\Downloads\nfirs_all_incident_pdr_2024.zip`

## Step-by-Step Instructions

### 1. Copy the File
```bash
# If using WSL
cp /mnt/c/Users/EU01242390/Downloads/nfirs_all_incident_pdr_2024.zip .

# Or from Windows: Copy the file to your ChrisCOMM directory
```

### 2. Extract the Data
```bash
cd /home/user/ChrisCOMM
unzip nfirs_all_incident_pdr_2024.zip -d data/
```

### 3. Check What Was Extracted
```bash
ls -lh data/
```

Common NFIRS file patterns:
- `basicincident.csv` or `BASICINCIDENT.csv`
- `fireincident.csv` or `FIREINCIDENT.csv`
- `structurefire.csv` or `STRUCTUREFIRE.csv`

### 4. Rename Files if Uppercase
```bash
cd data
for f in *.CSV; do mv "$f" "${f,,}"; done
cd ..
```

### 5. Verify the Data
```bash
python src/main.py stats --input data/basicincident.csv
```

Expected output:
- Total records
- Year range (should show 2024)
- Top incident types
- State distribution

### 6. Run the Analysis
```bash
# For 2024 solar panel and battery fires
python src/main.py analyze --type all --year 2024 --format html

# Or get all formats
python src/main.py analyze --type all --year 2024 --format all
```

### 7. Find Your Reports
```bash
ls -lah reports/
```

Reports will be in: `reports/YYYYMMDD_HHMMSS/`

### 8. Open the HTML Report
The HTML report will show:
- Total solar panel fire incidents in 2024
- Total lithium-ion battery fire incidents in 2024
- Deaths and injuries
- Property loss
- Geographic distribution
- Temporal trends
- Detailed incident characteristics

## Quick Commands Reference

```bash
# View NFIRS codes being used
python src/main.py check-codes --type all

# Solar panels only
python src/main.py analyze --type solar --year 2024

# Batteries only
python src/main.py analyze --type battery --year 2024

# Both types (default)
python src/main.py analyze --type all --year 2024

# All years in dataset
python src/main.py analyze --type all
```

## Expected Results

For 2024 NFIRS data, you should get:
- Filtered incidents matching solar panel criteria
- Filtered incidents matching battery criteria
- Analysis by:
  - Month/quarter (seasonal patterns)
  - State/region (geographic hotspots)
  - Incident subcategory (building fire, vehicle fire, etc.)
  - Casualties and property damage

## Troubleshooting

### "File not found"
- Check the file name matches exactly
- Verify you're in /home/user/ChrisCOMM directory
- Use `ls -la data/` to see actual filenames

### "No matching incidents"
- This is normal if 2024 had few solar/battery fires
- Try analyzing all years: `python src/main.py analyze --type all`
- Check codes: `python src/main.py check-codes --type all`

### "Column not found" errors
- NFIRS column names changed over years
- The workflow handles most variations
- Check if your data has the expected columns:
  ```bash
  head -1 data/basicincident.csv
  head -1 data/fireincident.csv
  ```

## What You'll Learn

From your 2024 NFIRS data analysis:
1. **How many solar panel fires occurred in 2024**
2. **How many lithium-ion battery fires (EVs, ESS, e-bikes)**
3. **Which states had the most incidents**
4. **Seasonal patterns (which months had most fires)**
5. **Common causes and ignition factors**
6. **Casualty and property loss statistics**
7. **Trends compared to previous periods**

## Need Help?

Run any command with `--help`:
```bash
python src/main.py --help
python src/main.py analyze --help
```
