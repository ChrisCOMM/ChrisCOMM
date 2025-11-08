# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Sample Data (for testing)
```bash
python src/main.py create-sample
```

### 3. Run Your First Analysis
```bash
python src/main.py analyze --type all --format html
```

### 4. View Your Report
Open the generated HTML report in `reports/<timestamp>/report.html`

## 📊 What You Get

The workflow analyzes NFIRS data to identify and report on:

### Solar Panel Fires
- Rooftop solar installations
- Ground-mounted solar arrays
- Solar farms
- PV system component failures

### Lithium-Ion Battery Fires
- Electric vehicle (EV) fires
- Energy storage systems (ESS/BESS)
- E-bike and e-scooter batteries
- Portable battery incidents

## 🎯 Common Use Cases

### Analyze a Specific Year
```bash
python src/main.py analyze --type all --year 2024
```

### Generate Only CSV Data
```bash
python src/main.py analyze --type battery --format csv
```

### Check NFIRS Codes Being Used
```bash
python src/main.py check-codes --type all
```

### View Data Statistics
```bash
python src/main.py stats --input data/basicincident.csv
```

## 📁 Project Structure

```
ChrisCOMM/
├── config/              # Configuration files
│   ├── nfirs_codes.yml       # NFIRS code mappings
│   └── workflow_config.yml   # Workflow settings
├── src/                 # Source code
│   ├── data_loader.py        # Data loading
│   ├── filters.py            # Incident filtering
│   ├── analyzers.py          # Data analysis
│   ├── reporters.py          # Report generation
│   └── main.py               # CLI interface
├── data/                # Input data (your NFIRS files)
├── reports/             # Generated reports
├── tests/               # Unit tests
└── .github/workflows/   # GitHub Actions automation
```

## 🔧 Configuration

### Customize NFIRS Codes
Edit `config/nfirs_codes.yml` to:
- Add new equipment codes
- Modify narrative keywords
- Adjust filtering criteria

### Adjust Workflow Settings
Edit `config/workflow_config.yml` to:
- Set alert thresholds
- Configure report formats
- Modify analysis options

## 🤖 GitHub Actions

The workflow automatically runs:
- **Weekly**: Every Sunday at midnight UTC
- **On Push**: When data/config/src files change
- **Manual**: Via GitHub Actions "Run workflow" button

### Manual Trigger
1. Go to your repository's Actions tab
2. Select "NFIRS Analysis Workflow"
3. Click "Run workflow"
4. Choose incident type and year
5. Download reports from artifacts

## 📈 Understanding Output

### HTML Report Includes:
- Executive summary with key metrics
- Temporal trends (yearly, monthly, quarterly)
- Geographic distribution by state/region
- Casualty analysis (deaths, injuries)
- Property loss statistics
- Incident characteristics

### CSV Export Contains:
- All filtered incident records
- Ready for Excel, R, Python analysis

### JSON Analysis Provides:
- Structured data for APIs
- Programmatic access to results

## 🆘 Need Help?

```bash
# Show all available commands
python src/main.py --help

# Show help for specific command
python src/main.py analyze --help
```

See [USAGE.md](USAGE.md) for detailed documentation.

## ⚡ Next Steps

1. **Get Real NFIRS Data**: Download from [FEMA OpenFEMA](https://www.fema.gov/about/openfema/data-sets)
2. **Customize Filters**: Adjust codes in `config/nfirs_codes.yml`
3. **Set Up Alerts**: Configure thresholds in `config/workflow_config.yml`
4. **Automate**: Enable GitHub Actions for regular monitoring

## 🎓 Learn More

- **Full Documentation**: [README.md](README.md)
- **Detailed Usage**: [USAGE.md](USAGE.md)
- **NFIRS Reference**: [NFIRS Complete Reference Guide](https://www.usfa.fema.gov/downloads/pdf/nfirs/NFIRS_Complete_Reference_Guide_2015.pdf)
