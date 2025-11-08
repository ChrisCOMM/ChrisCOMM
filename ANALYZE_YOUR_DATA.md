# How to Analyze Your NFIRS Data

## Quick Start with Your Zip File

### Method 1: Using the Setup Script

```bash
# Run the setup helper
./setup_nfirs_data.sh /path/to/your/nfirs_data.zip
```

### Method 2: Manual Extraction

```bash
# 1. Extract your zip file
unzip your_nfirs_data.zip -d data/

# 2. Check what files you have
ls -lh data/

# 3. Rename files if needed (NFIRS files are often uppercase)
cd data/
# If files are uppercase, rename them:
for file in *.CSV; do mv "$file" "$(echo $file | tr '[:upper:]' '[:lower:]')"; done
cd ..
```

## Common NFIRS File Names

Your zip file should contain files like:
- `basicincident.csv` (or `BASICINCIDENT.csv`) - **Required**
- `fireincident.csv` (or `FIREINCIDENT.csv`) - **Required for fire analysis**
- `structurefire.csv` (or `STRUCTUREFIRE.csv`) - Optional
- `hazmat.csv` - Optional
- `wildland.csv` - Optional

## Update Configuration (If Needed)

If your files have different names, edit `config/workflow_config.yml`:

```yaml
data_sources:
  nfirs_basic_module: "data/your_basic_file.csv"
  nfirs_fire_module: "data/your_fire_file.csv"
  nfirs_structure_module: "data/your_structure_file.csv"
```

## Step-by-Step Analysis

### 1. Verify Your Data

```bash
# Check basic module statistics
python src/main.py stats --input data/basicincident.csv
```

**Expected output:**
- Total records count
- Year range
- Top incident types
- Top states

### 2. Run Your First Analysis

```bash
# Analyze all solar panel and battery incidents
python src/main.py analyze --type all --format html
```

This will:
- ✅ Load your NFIRS data
- ✅ Filter for solar panel and battery fires
- ✅ Generate comprehensive analysis
- ✅ Create HTML report

### 3. View Your Report

```bash
# Find the latest report
ls -lt reports/

# The report is in: reports/YYYYMMDD_HHMMSS/report.html
# Open it in your browser
```

## Analysis Options

### Filter by Incident Type

```bash
# Only solar panel fires
python src/main.py analyze --type solar --format all

# Only battery fires
python src/main.py analyze --type battery --format all

# Both types (default)
python src/main.py analyze --type all --format all
```

### Filter by Year

```bash
# Analyze only 2023 data
python src/main.py analyze --type all --year 2023

# Analyze 2024 data
python src/main.py analyze --type all --year 2024
```

### Choose Report Format

```bash
# HTML report only
python src/main.py analyze --type all --format html

# CSV export only
python src/main.py analyze --type all --format csv

# JSON only
python src/main.py analyze --type all --format json

# All formats
python src/main.py analyze --type all --format all
```

### Specify Output Directory

```bash
# Save reports to custom location
python src/main.py analyze --type all --output my_reports/
```

## Understanding Your Results

### Reports Generated

1. **report.html** - Interactive HTML report with:
   - Executive summary
   - Temporal trends (charts)
   - Geographic distribution
   - Casualty analysis
   - Property loss statistics

2. **incidents.csv** - Raw filtered data for:
   - Excel analysis
   - Database import
   - Custom processing

3. **analysis.json** - Structured results for:
   - API integration
   - Custom dashboards
   - Further programming

## Troubleshooting

### Problem: "No data loaded"

**Solution:**
```bash
# Check if files exist
ls -lh data/*.csv

# Check file permissions
chmod 644 data/*.csv

# Verify file format
file data/basicincident.csv  # Should show "CSV text"
head -5 data/basicincident.csv  # Should show column headers
```

### Problem: "No matching incidents found"

**Possible causes:**
1. **Your data doesn't contain solar/battery incidents** - Normal for some datasets
2. **Check your data year range:**
   ```bash
   python src/main.py stats --input data/basicincident.csv
   ```

3. **Review NFIRS codes being used:**
   ```bash
   python src/main.py check-codes --type all
   ```

4. **Adjust filtering** in `config/nfirs_codes.yml`

### Problem: Column name errors

**Solution:** NFIRS column names vary by year and source.

Edit the code to handle your column names, or standardize your CSV columns:
- `STATE` → `state`
- `FDID` → `fdid`
- `INC_DATE` → `inc_date`
- `INC_NO` → `inc_no`

## Advanced Usage

### Multi-Year Analysis

```bash
# If you have multiple years of data
python src/main.py analyze --type all --format all
# This will analyze all years in your dataset
```

### Large Datasets

For files over 1GB, the workflow will automatically:
- Process data in chunks
- Show progress indicators
- Manage memory efficiently

### Custom Filtering

Edit `config/nfirs_codes.yml` to add custom codes:

```yaml
equipment_codes:
  solar_equipment:
    - 262   # Solar energy system
    - 999   # Add your custom codes here
```

## Example Workflow

```bash
# Complete analysis workflow
cd /home/user/ChrisCOMM

# 1. Extract data
unzip ~/Downloads/nfirs_2024.zip -d data/

# 2. Check data
python src/main.py stats --input data/basicincident.csv

# 3. View available codes
python src/main.py check-codes --type all

# 4. Run analysis
python src/main.py analyze --type all --year 2024 --format all

# 5. View results
ls -lah reports/*/

# 6. Open HTML report
# The path will be shown in the output: reports/YYYYMMDD_HHMMSS/report.html
```

## Getting Help

```bash
# Show all commands
python src/main.py --help

# Show help for analyze command
python src/main.py analyze --help

# Show help for other commands
python src/main.py stats --help
python src/main.py check-codes --help
python src/main.py create-sample --help
```

## Next Steps

1. ✅ Extract your NFIRS data
2. ✅ Run initial analysis
3. ✅ Review the HTML report
4. 📊 Customize codes for your needs
5. 🔄 Set up automated monitoring with GitHub Actions
6. 📧 Configure alerts for critical incidents

## Need More Help?

- Check the main [README.md](README.md)
- Read the detailed [USAGE.md](USAGE.md)
- Review [QUICKSTART.md](QUICKSTART.md)
- See NFIRS documentation: https://www.usfa.fema.gov/nfirs/

---

**Ready to analyze?** Just run:
```bash
python src/main.py analyze --type all
```
