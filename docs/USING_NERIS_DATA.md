# Using the ChrisCOMM Tool with Real NERIS Data

**Guide for Solar Panel & Lithium-Ion Battery Fire Analysis**

---

## Overview

This guide explains how to use the ChrisCOMM analysis tool with real-world NERIS (National Emergency Response Information System) data to analyze solar panel and lithium-ion battery fire incidents.

The tool now supports both:
- **NFIRS** (legacy format) - Data until February 2026
- **NERIS** (current format) - Data from 2024 onwards

---

## Table of Contents

1. [Getting NERIS Data](#getting-neris-data)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Running Analysis](#running-analysis)
5. [Understanding Results](#understanding-results)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

---

## Getting NERIS Data

### Option 1: NERIS API (Recommended)

**Pros:** Real-time data, automatic updates, easy filtering
**Cons:** Requires API access credentials

#### Step 1: Request API Access

Contact USFA/FSRI for API credentials:
- **NERIS Website:** https://neris.fsri.org
- **Helpdesk:** https://neris.atlassian.net/servicedesk/customer/portals
- **Email:** neris-support@fsri.org (check current contact info)

#### Step 2: Set API Key

```bash
# Set environment variable
export NERIS_API_KEY="your-api-key-here"

# Or add to your shell profile (~/.bashrc or ~/.zshrc)
echo 'export NERIS_API_KEY="your-api-key-here"' >> ~/.bashrc
```

#### Step 3: Configure for API Access

Edit `config/workflow_config.yml`:

```yaml
data_sources:
  # Enable NERIS API
  use_neris_api: true
  neris_api_endpoint: "https://api.neris.fsri.org/v1"
  neris_api_key: ${NERIS_API_KEY}  # Uses environment variable
```

### Option 2: NERIS File Downloads

**Pros:** No API access needed, works offline
**Cons:** Manual updates, larger file sizes

#### Step 1: Download NERIS Data Files

NERIS data may be available from:
- **FEMA OpenFEMA:** https://www.fema.gov/about/openfema/data-sets
- **NERIS Portal:** https://neris.fsri.org (check for data export)
- **State Fire Marshals:** Contact your state fire marshal's office

#### Step 2: Place Files in Data Directory

```bash
# NERIS files typically use ^ delimiter
data/
├── neris_incidents_2024.csv      # Incident data
├── neris_incidents_2025.csv
└── neris_incidents_2026.csv
```

#### Step 3: Configure for File Access

Edit `config/workflow_config.yml`:

```yaml
data_sources:
  # Disable API
  use_neris_api: false

  # Point to NERIS files
  nfirs_basic_module: "data/neris_incidents_2024.csv"
  nfirs_fire_module: "data/neris_incidents_2024.csv"
```

**Note:** NERIS combines basic and fire data in one file, so use the same path for both.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install pandas pyyaml requests numpy
```

### 2. Basic Analysis

```python
from src.data_loader import NFIRSDataLoader
from src.filters import NFIRSIncidentFilter
from src.analyzers import NFIRSAnalyzer

# Load data (auto-detects NFIRS vs NERIS)
loader = NFIRSDataLoader()
modules = loader.load_all_modules()
data = loader.merge_modules(modules)

# Filter for solar and battery incidents
filter_obj = NFIRSIncidentFilter()
incidents = filter_obj.filter_all_incidents(data)
incidents = filter_obj.add_subcategories(incidents)

# Analyze
analyzer = NFIRSAnalyzer()
results = analyzer.generate_summary_report(incidents)

# View results
print(f"Total incidents: {results['metadata']['total_incidents']}")
print(f"Format: {results['metadata']['data_format']}")

# NERIS-specific results (if available)
if 'neris_battery_analysis' in results:
    battery = results['neris_battery_analysis']
    print(f"Thermal runaway events: {battery['thermal_runaway']['count']}")
```

### 3. Command Line Usage

```bash
# Run analysis on all incident types
python src/main.py analyze --type all --output reports/

# Solar panel incidents only
python src/main.py analyze --type solar --year 2024 --output reports/

# Battery incidents only
python src/main.py analyze --type battery --year 2024 --output reports/
```

---

## Configuration

### Filtering Configuration

Edit `config/workflow_config.yml`:

```yaml
filtering:
  # Use NERIS structured fields when available
  strict_mode: false
  confidence_threshold: 0.6

  # Narrative keyword matching (fallback for NFIRS or incomplete NERIS)
  use_narrative_matching: true
  min_keyword_matches: 1

data_processing:
  start_year: 2024  # NERIS data available from 2024
  chunk_size: 10000
  parallel_processing: true
```

### Analysis Configuration

```yaml
analysis:
  trend_analysis: true
  trend_periods:
    - monthly
    - quarterly
    - yearly

  geographic_analysis: true
  casualty_analysis: true
  property_loss_analysis: true
```

### Alert Configuration

```yaml
alerts:
  enabled: true
  thresholds:
    incidents_per_month: 10
    any_fatalities: true
    injuries_threshold: 5
```

---

## Running Analysis

### Basic Analysis

```python
# Example: Analyze 2024 battery incidents
from src.data_loader import NFIRSDataLoader
from src.filters import NFIRSIncidentFilter
from src.analyzers import NFIRSAnalyzer

# Load 2024 data
loader = NFIRSDataLoader()
modules = loader.load_all_modules()
data = loader.merge_modules(modules)

# Filter for battery incidents
filter_obj = NFIRSIncidentFilter()
battery_incidents = filter_obj.filter_battery_incidents(data)
battery_incidents = filter_obj.add_subcategories(battery_incidents)

# Get statistics
stats = filter_obj.get_filter_statistics(battery_incidents)
print(f"Total battery incidents: {stats['total_incidents']}")
print(f"By subcategory: {stats['by_subcategory']}")

# NERIS-specific stats
if 'neris_features' in stats:
    print(f"\nNERIS Features:")
    print(f"  Thermal runaway: {stats['neris_features']['thermal_runaway_count']} ({stats['neris_features']['thermal_runaway_pct']}%)")
    print(f"  Charging-related: {stats['neris_features']['charging_related_count']} ({stats['neris_features']['charging_related_pct']}%)")
```

### NERIS-Specific Filters

```python
# Filter for thermal runaway events only
thermal_events = filter_obj.filter_thermal_runaway_incidents(battery_incidents)
print(f"Thermal runaway events: {len(thermal_events)}")

# Filter for charging-related fires
charging_fires = filter_obj.filter_charging_incidents(battery_incidents)
print(f"Charging-related fires: {len(charging_fires)}")
```

### Detailed Analysis

```python
# Full analysis with NERIS enhancements
analyzer = NFIRSAnalyzer()
results = analyzer.generate_summary_report(battery_incidents)

# Save results
import json
with open('reports/battery_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

# Access NERIS battery analysis
if 'neris_battery_analysis' in results:
    battery_analysis = results['neris_battery_analysis']

    # Thermal runaway statistics
    print(f"\nThermal Runaway:")
    print(f"  Count: {battery_analysis['thermal_runaway']['count']}")
    print(f"  Percentage: {battery_analysis['thermal_runaway']['percentage']}%")

    # Product type breakdown
    print(f"\nProduct Categories:")
    for category, count in battery_analysis['product_categories'].items():
        print(f"  {category}: {count}")

    # Safety certification
    print(f"\nSafety Certification:")
    cert = battery_analysis['safety_certification']
    print(f"  Safety listed: {cert['safety_listed']}")
    print(f"  Not safety listed: {cert['not_safety_listed']}")
    print(f"  Percentage unsafe: {cert['percentage_unsafe']}%")
```

---

## Understanding Results

### NERIS Data Format Detection

The tool automatically detects whether data is NFIRS or NERIS format:

```python
# Check detected format
print(f"Data format: {results['metadata']['data_format']}")
# Output: "NERIS" or "NFIRS"
```

### NERIS Battery Analysis Results

When NERIS data is available, battery analysis includes:

```json
{
  "neris_battery_analysis": {
    "total_battery_incidents": 150,
    "thermal_runaway": {
      "count": 45,
      "percentage": 30.0,
      "incidents_with_thermal_runaway": 45,
      "incidents_without_thermal_runaway": 105
    },
    "charging_analysis": {
      "charging_related": 60,
      "not_charging": 80,
      "unknown": 10,
      "percentage_charging": 40.0
    },
    "chemistry_breakdown": {
      "LITHIUM_ION": 120,
      "LIFEPO4": 20,
      "LITHIUM_POLYMER": 10
    },
    "product_categories": {
      "E-Mobility": 50,
      "Electric Vehicles": 40,
      "Energy Storage Systems": 30,
      "Consumer Products": 30
    },
    "safety_certification": {
      "safety_listed": 80,
      "not_safety_listed": 60,
      "unknown": 10,
      "percentage_unsafe": 42.9
    },
    "specifications": {
      "watt_hour": {
        "mean": 250.5,
        "median": 180.0,
        "min": 10.0,
        "max": 85000.0
      }
    }
  }
}
```

### NERIS Solar/PV Analysis Results

```json
{
  "neris_pv_analysis": {
    "total_pv_incidents": 85,
    "pv_type_breakdown": {
      "PANEL_POWER_GENERATION": 70,
      "TILE_POWER_GENERATION": 10,
      "THIN_FILM_POWER_GENERATION": 5
    },
    "ignition_classification": {
      "pv_was_ignition_source": 60,
      "pv_was_fire_target": 20,
      "unknown": 5,
      "percentage_pv_caused": 75.0
    }
  }
}
```

**Key Insight:** `percentage_pv_caused` tells you what % of fires were CAUSED by the PV system (vs. fires that spread TO the PV system).

---

## Advanced Usage

### API Query Parameters

```python
# Query specific date range and incident types
from src.data_loader import NFIRSDataLoader

loader = NFIRSDataLoader()
modules = loader.load_from_neris_api(
    start_date='2024-01-01',
    end_date='2024-12-31',
    incident_type='FIRE',
    limit=50000
)

data = loader.merge_modules(modules)
```

### Custom Filtering

```python
# Filter for specific product types
e_bike_fires = battery_incidents[
    battery_incidents['product_type'].str.contains('POWER_ASSISTED_BICYCLE', na=False)
]

e_scooter_fires = battery_incidents[
    battery_incidents['product_type'].str.contains('ELECTRIC_SCOOTER', na=False)
]

ev_fires = battery_incidents[
    battery_incidents['product_type'].str.contains('ELECTRIC_VEHICLE', na=False)
]

print(f"E-bike fires: {len(e_bike_fires)}")
print(f"E-scooter fires: {len(e_scooter_fires)}")
print(f"EV fires: {len(ev_fires)}")
```

### Thermal Runaway Analysis

```python
# Analyze thermal runaway patterns
thermal_events = battery_incidents[battery_incidents['thermal_runaway'] == True]

# By product type
thermal_by_product = thermal_events.groupby('product_type').size().to_dict()
print("Thermal runaway by product:")
for product, count in thermal_by_product.items():
    print(f"  {product}: {count}")

# Thermal runaway while charging
thermal_charging = thermal_events[thermal_events['charging_at_ignition'] == True]
print(f"\nThermal runaway while charging: {len(thermal_charging)} ({len(thermal_charging)/len(thermal_events)*100:.1f}%)")
```

### Solar PV Causation Analysis

```python
# Analyze PV as ignition source
solar_incidents = filter_obj.filter_solar_incidents(data)

# Count fires CAUSED by PV
pv_source = solar_incidents[solar_incidents['pv_ignition_type'] == 'SOURCE']
pv_target = solar_incidents[solar_incidents['pv_ignition_type'] == 'TARGET']

print(f"Fires caused BY solar PV: {len(pv_source)}")
print(f"Fires spread TO solar PV: {len(pv_target)}")
print(f"PV causation rate: {len(pv_source)/(len(pv_source)+len(pv_target))*100:.1f}%")
```

---

## Troubleshooting

### Issue: "No NERIS fields detected"

**Cause:** Data is in NFIRS format or NERIS fields are missing

**Solution:**
1. Check your data source - is it actually NERIS data?
2. Verify file delimiter (NERIS uses `^`, NFIRS uses `,`)
3. Check column names - NERIS has `thermal_runaway`, `pv_type`, etc.

```python
# Check what format was detected
print(f"Detected format: {loader.data_format}")

# Check available columns
print(f"Columns: {list(data.columns)}")
```

### Issue: "API authentication failed"

**Cause:** Missing or invalid API key

**Solution:**
```bash
# Verify API key is set
echo $NERIS_API_KEY

# Test API access
curl -H "Authorization: Bearer $NERIS_API_KEY" \
     https://api.neris.fsri.org/v1/incidents?limit=1
```

### Issue: "Merged dataset contains 1 column"

**Cause:** Delimiter mismatch

**Solution:**
The data loader now auto-detects delimiters. If it fails:

```python
# Force delimiter
df = pd.read_csv('data/neris_incidents.csv', sep='^', low_memory=False)
```

### Issue: "Empty results"

**Cause:** No incidents match filter criteria

**Solution:**
Check what's being filtered:

```python
# Check total records
print(f"Total records loaded: {len(data)}")

# Check incident types
if 'incident_type_value1' in data.columns:
    print(f"Incident types: {data['incident_type_value1'].value_counts()}")

# Check for NERIS battery fields
if 'product_type' in data.columns:
    print(f"Product types: {data['product_type'].value_counts()}")
```

---

## Data Quality Considerations

### NERIS Data Advantages

✅ **Thermal runaway** - Boolean field (100% accurate)
✅ **Charging status** - Direct field (no text parsing)
✅ **Product type** - Hierarchical codes (e-bike vs e-scooter distinction)
✅ **Battery chemistry** - Structured field
✅ **Safety certification** - Direct field
✅ **PV ignition** - SOURCE vs TARGET classification

### Potential Issues

⚠️ **Optional fields** - Not all incidents have all NERIS fields
⚠️ **Transition period** - Some 2024 data may still be NFIRS format
⚠️ **Data entry variance** - Quality depends on reporting department

### Best Practices

1. **Check field availability** before analysis:
   ```python
   if 'thermal_runaway' in data.columns:
       # Use NERIS thermal runaway field
   else:
       # Fall back to narrative keywords
   ```

2. **Use both methods** during transition:
   ```python
   # NERIS structured field
   neris_battery = data[data['product_type'].str.contains('E_MOBILITY', na=False)]

   # Plus narrative fallback
   narrative_battery = data[data['narrative'].str.contains('e-bike', na=False, case=False)]

   # Combine
   all_ebikes = pd.concat([neris_battery, narrative_battery]).drop_duplicates()
   ```

3. **Validate results** against known incidents

---

## Example Analysis Workflow

Here's a complete real-world analysis workflow:

```python
#!/usr/bin/env python
"""
Analyze 2024 E-Bike Fire Incidents with NERIS Data
"""
import pandas as pd
from src.data_loader import NFIRSDataLoader
from src.filters import NFIRSIncidentFilter
from src.analyzers import NFIRSAnalyzer

# 1. Load 2024 NERIS data
print("Loading NERIS data...")
loader = NFIRSDataLoader()
modules = loader.load_all_modules()
data = loader.merge_modules(modules)
print(f"Loaded {len(data)} incidents")

# 2. Filter for battery incidents
print("\nFiltering for battery incidents...")
filter_obj = NFIRSIncidentFilter()
battery_incidents = filter_obj.filter_battery_incidents(data)
battery_incidents = filter_obj.add_subcategories(battery_incidents)
print(f"Found {len(battery_incidents)} battery incidents")

# 3. Extract e-bike incidents
print("\nFiltering for e-bikes...")
ebikes = battery_incidents[battery_incidents['subcategory'] == 'e_bike']
print(f"Found {len(ebikes)} e-bike incidents")

# 4. Analyze thermal runaway
if 'thermal_runaway' in ebikes.columns:
    thermal = ebikes[ebikes['thermal_runaway'] == True]
    print(f"\nThermal runaway: {len(thermal)} ({len(thermal)/len(ebikes)*100:.1f}%)")

# 5. Analyze charging status
if 'charging_at_ignition' in ebikes.columns:
    charging = ebikes[ebikes['charging_at_ignition'] == True]
    print(f"Charging at ignition: {len(charging)} ({len(charging)/len(ebikes)*100:.1f}%)")

# 6. Safety certification
if 'safety_listed' in ebikes.columns:
    unsafe = ebikes[ebikes['safety_listed'] == False]
    print(f"Not safety listed: {len(unsafe)} ({len(unsafe)/len(ebikes)*100:.1f}%)")

# 7. Full analysis
print("\nGenerating full analysis...")
analyzer = NFIRSAnalyzer()
results = analyzer.generate_summary_report(ebikes)

# 8. Save results
import json
with open('reports/ebike_analysis_2024.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to reports/ebike_analysis_2024.json")
```

---

## Resources

- **NERIS Website:** https://neris.fsri.org
- **NERIS API Documentation:** https://api.neris.fsri.org/v1/docs
- **NERIS GitHub:** https://github.com/ulfsri/neris-framework
- **NERIS Helpdesk:** https://neris.atlassian.net/servicedesk
- **NFIRS (Legacy):** https://www.usfa.fema.gov/nfirs/

---

## Summary

The ChrisCOMM tool now provides:

1. **Automatic format detection** - Works with NFIRS and NERIS
2. **NERIS-specific analysis** - Thermal runaway, charging, chemistry
3. **Enhanced categorization** - E-bikes, e-scooters, EVs, ESS
4. **PV causation analysis** - Fires caused BY vs TO solar
5. **Safety insights** - UL certification, battery specifications
6. **Flexible data access** - API or file-based

Start analyzing your NERIS data today to gain unprecedented insights into battery and solar fire incidents!

---

**Last Updated:** March 26, 2026
**NERIS Version:** Beta (May 2024)
**Tool Version:** 2.0.0
