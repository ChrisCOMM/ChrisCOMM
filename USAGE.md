# NFIRS Workflow Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ChrisCOMM/ChrisCOMM.git
cd ChrisCOMM

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Data

Place your NFIRS data files in the `data/` directory:

```
data/
├── basicincident.csv      # NFIRS Basic Module
├── fireincident.csv       # NFIRS Fire Module
└── structurefire.csv      # NFIRS Structure Fire Module (optional)
```

**Obtaining NFIRS Data:**
- [FEMA OpenFEMA Data Sets](https://www.fema.gov/about/openfema/data-sets)
- State fire marshal offices
- Local fire department records

### 3. Run Analysis

#### Analyze All Incident Types
```bash
python src/main.py analyze --input data/basicincident.csv --type all
```

#### Analyze Only Solar Panel Incidents
```bash
python src/main.py analyze --input data/basicincident.csv --type solar
```

#### Analyze Only Battery Incidents
```bash
python src/main.py analyze --input data/basicincident.csv --type battery
```

#### Filter by Year
```bash
python src/main.py analyze --input data/basicincident.csv --type all --year 2024
```

#### Specify Output Format
```bash
# Generate only HTML report
python src/main.py analyze --input data/basicincident.csv --format html

# Generate only CSV export
python src/main.py analyze --input data/basicincident.csv --format csv

# Generate all formats
python src/main.py analyze --input data/basicincident.csv --format all
```

## Command Reference

### create-sample
Create sample NFIRS data for testing

```bash
python src/main.py create-sample --output-dir data
```

### analyze
Main analysis command

```bash
python src/main.py analyze [OPTIONS]
```

**Options:**
- `--input, -i`: Path to NFIRS basic module CSV file
- `--type, -t`: Type of incidents (`solar`, `battery`, `all`)
- `--year, -y`: Filter by specific year
- `--output, -o`: Output directory for reports (default: `reports`)
- `--format, -f`: Report format (`html`, `csv`, `json`, `txt`, `all`)

### stats
Display statistics about NFIRS data file

```bash
python src/main.py stats --input data/basicincident.csv
```

### check-codes
Display NFIRS codes used for filtering

```bash
# Show all codes
python src/main.py check-codes --type all

# Show only solar codes
python src/main.py check-codes --type solar

# Show only battery codes
python src/main.py check-codes --type battery
```

## Configuration

### NFIRS Codes Configuration
Edit `config/nfirs_codes.yml` to customize:
- Incident type codes
- Equipment codes
- Heat source codes
- Narrative keywords
- Other filtering criteria

### Workflow Configuration
Edit `config/workflow_config.yml` to customize:
- Data processing settings
- Filtering thresholds
- Analysis options
- Report formats
- Alert thresholds

## GitHub Actions Automation

The workflow is configured to run automatically:

### Scheduled Execution
Runs weekly every Sunday at midnight UTC

### Manual Trigger
1. Go to Actions tab in GitHub
2. Select "NFIRS Analysis Workflow"
3. Click "Run workflow"
4. Select incident type and optional year filter
5. Click "Run workflow"

### Automatic Execution
Runs on push to main branch when files in these directories change:
- `data/`
- `config/`
- `src/`

## Understanding the Output

### HTML Report
Interactive report with:
- Executive summary
- Temporal trends
- Geographic distribution
- Casualty analysis
- Property loss analysis
- Incident characteristics

### CSV Export
Raw filtered incident data for further analysis in Excel, R, Python, etc.

### JSON Analysis
Structured analysis results for programmatic access

### Text Summary
Plain text summary for quick review

## Examples

### Example 1: Annual Solar Panel Fire Report
```bash
python src/main.py analyze \
  --input data/basicincident.csv \
  --type solar \
  --year 2023 \
  --output reports/solar_2023 \
  --format all
```

### Example 2: EV Battery Fire Trend Analysis
```bash
python src/main.py analyze \
  --input data/basicincident.csv \
  --type battery \
  --output reports/battery_trends \
  --format html
```

### Example 3: Comprehensive Analysis
```bash
python src/main.py analyze \
  --input data/basicincident.csv \
  --type all \
  --output reports/comprehensive \
  --format all
```

## Troubleshooting

### No Data Found
- Verify data files are in the correct location
- Check file format (must be CSV)
- Ensure column names match NFIRS standards
- Try creating sample data: `python src/main.py create-sample`

### No Incidents Match Filters
- Review NFIRS codes: `python src/main.py check-codes`
- Check if your data includes the relevant codes
- Adjust filtering criteria in `config/nfirs_codes.yml`
- Enable narrative matching in `config/workflow_config.yml`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (requires 3.8+)
- Verify you're running from the project root directory

### GitHub Actions Failing
- Check workflow logs for specific errors
- Verify all configuration files are present
- Ensure data files are accessible (or download step is configured)

## Advanced Usage

### Custom Filtering

Edit `config/nfirs_codes.yml` to add custom codes:

```yaml
equipment_codes:
  solar_equipment:
    - 262   # Solar energy system
    - 999   # Your custom code
```

### Programmatic Access

```python
from src.data_loader import NFIRSDataLoader
from src.filters import NFIRSIncidentFilter
from src.analyzers import NFIRSAnalyzer
from src.reporters import NFIRSReporter

# Load data
loader = NFIRSDataLoader()
modules = loader.load_all_modules()
merged_data = loader.merge_modules(modules)

# Filter incidents
incident_filter = NFIRSIncidentFilter()
filtered = incident_filter.filter_all_incidents(merged_data)

# Analyze
analyzer = NFIRSAnalyzer()
analysis = analyzer.generate_summary_report(filtered)

# Generate reports
reporter = NFIRSReporter(output_dir='custom_reports')
reports = reporter.generate_all_reports(filtered, analysis)
```

### Custom Analysis

Extend the `NFIRSAnalyzer` class:

```python
from src.analyzers import NFIRSAnalyzer

class CustomAnalyzer(NFIRSAnalyzer):
    def my_custom_analysis(self, df):
        # Your custom analysis logic
        return results
```

## Best Practices

1. **Data Management**
   - Keep raw NFIRS data in `data/` directory
   - Never commit large data files to Git
   - Use `.gitignore` to exclude data files

2. **Regular Updates**
   - Update NFIRS data regularly (quarterly recommended)
   - Review and update filtering codes as NFIRS standards evolve
   - Monitor GitHub Actions for automated runs

3. **Alert Thresholds**
   - Adjust alert thresholds in `config/workflow_config.yml`
   - Set up email notifications for critical alerts
   - Review alerts promptly

4. **Report Archival**
   - Archive important reports outside the workflow
   - Use GitHub Actions artifacts for temporary storage (90 days)
   - Export critical findings to long-term storage

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review existing documentation
- Check NFIRS documentation: [NFIRS](https://www.usfa.fema.gov/nfirs/)

## Additional Resources

- [NFIRS Complete Reference Guide](https://www.usfa.fema.gov/downloads/pdf/nfirs/NFIRS_Complete_Reference_Guide_2015.pdf)
- [FEMA OpenFEMA](https://www.fema.gov/about/openfema)
- [Fire Data Analysis Handbook](https://www.usfa.fema.gov/data/library.html)
