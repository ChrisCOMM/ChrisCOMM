# NFIRS Solar Panel & Lithium-Ion Battery Fire Analysis

A comprehensive workflow for monitoring and analyzing fire incidents involving solar panels and lithium-ion batteries using NFIRS (National Fire Incident Reporting System) data.

## Overview

This project provides automated tools to:
- Filter NFIRS data for incidents involving solar panels and lithium-ion batteries
- Analyze trends and patterns in these specific fire types
- Generate reports and visualizations
- Monitor new incidents and provide alerts

## Target Incident Types

### Solar Panel Fires
- Rooftop solar installations
- Ground-mounted solar arrays
- Solar thermal systems
- PV system component failures

### Lithium-Ion Battery Fires
- Electric vehicle (EV) battery fires
- Energy storage systems (ESS/BESS)
- Portable battery fires
- E-bike and e-scooter batteries

## NFIRS Data Fields Used

The workflow analyzes the following NFIRS modules:
- **Basic Module**: Incident type, date, location
- **Fire Module**: Area of origin, ignition factors, heat source
- **Structure Fire Module**: Structure type, material involved
- **Wildland Fire Module**: For solar farms
- **Hazmat Module**: Battery chemical releases
- **Equipment Module**: Specific equipment involved

## Project Structure

```
.
├── config/
│   ├── nfirs_codes.yml          # NFIRS code mappings
│   └── workflow_config.yml      # Workflow configuration
├── src/
│   ├── data_loader.py           # NFIRS data ingestion
│   ├── filters.py               # Incident filtering logic
│   ├── analyzers.py             # Data analysis functions
│   ├── reporters.py             # Report generation
│   └── main.py                  # Main workflow orchestrator
├── .github/
│   └── workflows/
│       └── nfirs_analysis.yml   # GitHub Actions workflow
├── tests/
│   └── test_filters.py          # Unit tests
├── reports/                      # Generated reports output
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Analysis
```bash
python src/main.py --input data/nfirs_data.csv --output reports/
```

### Filter Specific Incident Types
```bash
# Solar panel incidents only
python src/main.py --type solar --year 2024

# Lithium-ion battery incidents only
python src/main.py --type battery --year 2024

# Both types
python src/main.py --type all --year 2024
```

### Generate Reports
```bash
python src/main.py --report summary
python src/main.py --report detailed --format pdf
```

## Key Features

- **Automated Filtering**: Identifies relevant incidents using NFIRS codes
- **Trend Analysis**: Tracks incidents over time by type and location
- **Geospatial Mapping**: Visualizes incident locations
- **Equipment Analysis**: Identifies specific equipment/battery types involved
- **Cause Analysis**: Analyzes ignition factors and contributing factors
- **Custom Alerts**: Configurable alerts for incident thresholds

## NFIRS Codes Reference

### Relevant Incident Type Codes
- 111: Building fire
- 113: Cooking fire, confined to container
- 118: Trash or rubbish fire, contained
- 130-138: Mobile property fires (vehicles)
- 140-143: Natural vegetation fires

### Equipment Involved Codes
- Solar panels: 262 (Solar energy system)
- Batteries: 126 (Battery charger), 919 (Battery)

### Heat Source Codes
- 82: Battery
- 87: Solar energy collection system

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT License

## Data Sources

NFIRS data is available from:
- [FEMA NFIRS](https://www.fema.gov/about/openfema/data-sets)
- State fire marshal offices
- Local fire departments

## Disclaimer

This tool is for analysis purposes only. Always verify findings with original NFIRS data.
