# CLAUDE.md - AI Assistant Guide for ChrisCOMM Repository

## Overview

This document provides comprehensive guidance for AI assistants (like Claude Code) working with the ChrisCOMM repository. It covers codebase structure, development workflows, coding conventions, and key patterns to follow.

**Project**: NFIRS Solar Panel & Lithium-Ion Battery Fire Analysis
**Purpose**: Monitor and analyze fire incidents involving solar panels and lithium-ion batteries using NFIRS (National Fire Incident Reporting System) data
**Language**: Python 3.8+
**Architecture**: Modular CLI application with YAML configuration

---

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Codebase Structure](#codebase-structure)
3. [Core Components](#core-components)
4. [Development Workflows](#development-workflows)
5. [Coding Conventions](#coding-conventions)
6. [Configuration Management](#configuration-management)
7. [Testing Strategy](#testing-strategy)
8. [Git Workflow](#git-workflow)
9. [Common Tasks](#common-tasks)
10. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Architecture

### Design Philosophy

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Configuration-Driven**: NFIRS codes and workflow parameters are externalized to YAML files
- **Extensible**: Easy to add new incident types, codes, or analysis methods
- **Production-Ready**: Comprehensive logging, error handling, and testing

### Module Responsibilities

```
src/
├── data_loader.py    → Data ingestion and preprocessing
├── filters.py        → Incident filtering and categorization
├── analyzers.py      → Statistical analysis and trend detection
├── reporters.py      → Multi-format report generation
└── main.py           → CLI orchestrator and workflow coordination
```

### Data Flow

```
NFIRS CSV Files → NFIRSDataLoader → Merged Dataset
                                         ↓
                            NFIRSIncidentFilter → Filtered Incidents
                                         ↓
                              NFIRSAnalyzer → Analysis Results
                                         ↓
                              NFIRSReporter → Reports (HTML/CSV/JSON/TXT)
```

---

## Codebase Structure

### Directory Layout

```
ChrisCOMM/
├── .github/workflows/          # GitHub Actions automation
│   └── nfirs_analysis.yml     # CI/CD pipeline (244 lines)
├── config/                     # Configuration files
│   ├── nfirs_codes.yml        # NFIRS code mappings (4.6 KB)
│   └── workflow_config.yml    # Workflow settings (2.9 KB)
├── src/                        # Source code (2,058 lines total)
│   ├── data_loader.py         # Data loading (323 lines)
│   ├── filters.py             # Filtering logic (356 lines)
│   ├── analyzers.py           # Analysis functions (468 lines)
│   ├── reporters.py           # Report generation (511 lines)
│   └── main.py                # CLI interface (261 lines)
├── tests/                      # Unit tests
│   └── test_filters.py        # Filter tests (139 lines)
├── data/                       # Input data (gitignored)
│   └── .gitkeep
├── reports/                    # Generated reports (gitignored)
│   └── .gitkeep
├── logs/                       # Log files (gitignored)
├── Documentation/              # User guides (1,722 lines total)
│   ├── README.md              # Project overview
│   ├── QUICKSTART.md          # 5-minute guide
│   ├── USAGE.md               # Detailed usage
│   ├── PROJECT_SUMMARY.md     # Features and architecture
│   ├── ANALYZE_YOUR_DATA.md   # Data analysis guide
│   ├── MANUAL_ANALYSIS_STEPS.md
│   ├── FIX_SLOW_ANALYSIS.md   # Performance troubleshooting
│   └── GIT_WORKFLOW.md        # Git best practices
├── Scripts/
│   ├── extract_and_analyze.sh # Linux/Mac automation
│   ├── setup_nfirs_data.sh    # Data setup script
│   ├── analyze_nfirs.ps1      # Windows PowerShell
│   └── analyze_windows.bat    # Windows batch
├── requirements.txt            # Python dependencies
└── .gitignore                 # Git ignore rules
```

### File Metrics

| Category | Lines | Files |
|----------|-------|-------|
| Python Source Code | 2,058 | 5 modules + 1 test |
| Documentation | 1,722 | 8 markdown files |
| Configuration | ~300 | 2 YAML files |
| Automation | ~244 | 1 workflow + 4 scripts |

---

## Core Components

### 1. Data Loader (`src/data_loader.py`)

**Purpose**: Load and preprocess NFIRS data modules

**Key Class**: `NFIRSDataLoader`

**Main Methods**:
- `load_basic_module(path)` - Load basic incident data
- `load_fire_module(path)` - Load fire module data
- `load_structure_module(path)` - Load structure fire data
- `load_all_modules()` - Load all available modules
- `merge_modules(modules)` - Merge data sources on incident IDs

**Data Format Support**:
- Comma-delimited CSV (standard)
- Caret-delimited (^) for NERIS/NFIRS format
- Automatic delimiter detection
- Chunked processing for large files

**Helper Functions**:
- `create_sample_data(output_dir)` - Generate test data

**Important Notes**:
- Handles both lowercase and uppercase column names
- Preprocesses date fields and standardizes formats
- Supports partial module loading (graceful degradation)

### 2. Filters (`src/filters.py`)

**Purpose**: Identify and categorize relevant fire incidents

**Key Class**: `NFIRSIncidentFilter`

**Main Methods**:
- `filter_solar_incidents(df)` - Filter solar panel fires
- `filter_battery_incidents(df)` - Filter lithium-ion battery fires
- `filter_all_incidents(df)` - Filter both types
- `add_subcategories(df)` - Add detailed categorization

**Filtering Criteria**:
1. **Code-Based**: Equipment codes, heat source codes, incident type codes
2. **Narrative Text**: Keyword matching in incident descriptions
3. **Hybrid**: Combination of codes and keywords

**Subcategories Detected**:
- Solar: rooftop, ground_mounted, solar_farm, inverter
- Battery: EV, ESS, e_bike, e_scooter, portable, building_fire, vehicle_fire

**Configuration Source**: `config/nfirs_codes.yml`

### 3. Analyzers (`src/analyzers.py`)

**Purpose**: Generate statistical analysis and insights

**Key Class**: `NFIRSAnalyzer`

**Main Methods**:
- `temporal_analysis(df)` - Yearly, monthly, quarterly, daily trends
- `geographic_analysis(df)` - State and regional distribution
- `casualty_analysis(df)` - Deaths and injury statistics
- `property_loss_analysis(df)` - Financial impact assessment
- `incident_characteristics(df)` - Causes, equipment, origins
- `generate_summary_report(df)` - Comprehensive analysis bundle

**Output Format**: Nested dictionaries with:
- Time series data
- Growth rates and trends
- Top N rankings
- Statistical summaries

### 4. Reporters (`src/reporters.py`)

**Purpose**: Generate multi-format reports

**Key Class**: `NFIRSReporter`

**Main Methods**:
- `generate_html_report(df, analysis)` - Interactive HTML with Plotly charts
- `generate_csv_report(df)` - Excel-compatible CSV export
- `generate_json_report(analysis)` - API-compatible JSON
- `generate_summary_text(analysis)` - Plain text summary
- `generate_all_reports(df, analysis)` - All formats simultaneously

**Report Features**:
- Timestamped output directories
- Interactive visualizations (Plotly)
- Jinja2 HTML templates
- Configurable detail levels

### 5. CLI Interface (`src/main.py`)

**Purpose**: Command-line orchestration

**Framework**: Click (declarative CLI)

**Commands**:
```bash
python src/main.py create-sample   # Generate test data
python src/main.py analyze         # Run analysis pipeline
python src/main.py stats           # Display data statistics
python src/main.py check-codes     # Show NFIRS codes
```

**Common Options**:
- `--input, -i` - Input file path
- `--type, -t` - Incident type (solar/battery/all)
- `--year, -y` - Filter by year
- `--output, -o` - Output directory
- `--format, -f` - Report format
- `--log-level` - Logging verbosity

**Logging**:
- Console output (stdout)
- File logging (`logs/nfirs_workflow.log`)
- Configurable levels (DEBUG/INFO/WARNING/ERROR/CRITICAL)

---

## Development Workflows

### Local Development Workflow

1. **Environment Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

2. **Development Cycle**
```bash
# Create sample data for testing
python src/main.py create-sample

# Test changes
python src/main.py analyze --type all

# Run unit tests
pytest tests/

# Check code quality
python -m py_compile src/*.py
```

3. **Testing with Real Data**
```bash
# Place NFIRS data in data/ directory
# Run analysis
python src/main.py analyze --input data/basicincident.csv --type all
```

### GitHub Actions Workflow

**Workflow File**: `.github/workflows/nfirs_analysis.yml`

**Trigger Mechanisms**:
1. **Scheduled**: Weekly (Sundays at midnight UTC)
2. **Manual**: Via "Run workflow" button with parameters
3. **Automatic**: On push to main when `data/`, `config/`, or `src/` change

**Jobs**:
1. `analyze-nfirs-data`: Main analysis pipeline
2. `test-workflow`: Comprehensive testing suite

**Artifacts**:
- Analysis reports (90-day retention)
- Alert summaries
- GitHub issues for critical findings

---

## Coding Conventions

### Python Style Guide

**Standard**: PEP 8 (Python Enhancement Proposal 8)

**Key Conventions**:

1. **Imports**
```python
# Standard library imports first
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any

# Third-party imports
import pandas as pd
import numpy as np
import click

# Local imports
from data_loader import NFIRSDataLoader
from filters import NFIRSIncidentFilter
```

2. **Type Hints**
```python
def analyze_data(df: pd.DataFrame, year: Optional[int] = None) -> Dict[str, Any]:
    """Analyze NFIRS data with optional year filter."""
    pass
```

3. **Docstrings**
```python
def filter_incidents(df, codes):
    """
    Filter incidents by NFIRS equipment codes.

    Args:
        df (pd.DataFrame): Input data
        codes (List[int]): NFIRS equipment codes

    Returns:
        pd.DataFrame: Filtered incidents
    """
```

4. **Logging**
```python
logger = logging.getLogger(__name__)
logger.info("Processing data...")
logger.warning("Missing column: %s", column_name)
logger.error("Failed to load file: %s", error)
```

5. **Error Handling**
```python
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return None
except pd.errors.ParserError as e:
    logger.error(f"Failed to parse CSV: {e}")
    return None
```

6. **Configuration Access**
```python
import yaml

with open('config/nfirs_codes.yml', 'r') as f:
    config = yaml.safe_load(f)

equipment_codes = config['equipment_codes']['solar_equipment']
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `NFIRSDataLoader` |
| Functions | snake_case | `load_basic_module()` |
| Variables | snake_case | `merged_data` |
| Constants | UPPER_CASE | `DEFAULT_YEAR` |
| Private | _leading_underscore | `_preprocess_data()` |
| Config Files | snake_case.yml | `nfirs_codes.yml` |

### Code Organization

**File Structure Pattern**:
```python
#!/usr/bin/env python3
"""Module docstring explaining purpose."""

# Imports
import ...

# Constants
DEFAULT_VALUE = 100

# Classes
class MyClass:
    """Class docstring."""

    def __init__(self):
        """Initialize instance."""
        pass

    def public_method(self):
        """Public method."""
        pass

    def _private_method(self):
        """Private helper method."""
        pass

# Helper Functions
def helper_function():
    """Helper function."""
    pass

# Main execution
if __name__ == '__main__':
    main()
```

---

## Configuration Management

### NFIRS Codes (`config/nfirs_codes.yml`)

**Structure**:
```yaml
incident_types:
  building_fire:
    - 111  # Building fire
    - 112  # Fires in structure other than in a building

equipment_codes:
  solar_equipment:
    - 262  # Solar energy system
  battery_equipment:
    - 919  # Battery (general)

heat_sources:
  solar: 87
  battery: 82

narrative_keywords:
  solar:
    - "solar panel"
    - "photovoltaic"
    - "PV system"
  battery:
    - "lithium"
    - "li-ion"
    - "thermal runaway"
```

**Usage Pattern**:
```python
import yaml

with open('config/nfirs_codes.yml', 'r') as f:
    codes = yaml.safe_load(f)

solar_codes = codes['equipment_codes']['solar_equipment']
```

### Workflow Configuration (`config/workflow_config.yml`)

**Key Sections**:
1. **Data Processing**: Chunk size, parallel workers
2. **Filtering**: Strict mode, confidence threshold
3. **Analysis**: Enabled features, time periods
4. **Reporting**: Formats, chart types, detail levels
5. **Alerts**: Thresholds for notifications
6. **Output**: Directories, timestamps, compression

**Best Practices**:
- **Never hardcode values** that might change (use config)
- **Document all settings** with inline comments
- **Use sensible defaults** that work for most cases
- **Validate config on load** to catch errors early

---

## Testing Strategy

### Unit Tests

**Framework**: pytest

**Test File**: `tests/test_filters.py`

**Coverage**:
- Incident filtering logic
- Subcategory assignment
- Statistics generation
- Edge cases and error handling

**Running Tests**:
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_filters.py::test_solar_filtering
```

### Integration Testing

**Via GitHub Actions**: Full workflow testing with sample data

**Manual Integration Test**:
```bash
# Generate sample data
python src/main.py create-sample

# Run full analysis
python src/main.py analyze --type all

# Verify outputs
ls reports/
```

### Test Data

**Sample Data Generator**: `create_sample_data()` in `src/data_loader.py`

**Includes**:
- Solar panel incidents (rooftop, ground-mounted, inverter)
- Battery incidents (EV, ESS, e-bike)
- Various incident types, dates, locations
- Realistic NFIRS field values

---

## Git Workflow

### Branch Strategy

**Main Branch**: `main` (or `master`)
**Feature Branches**: `claude/description-sessionid` (for AI assistants)
**Pattern**: `claude/claude-md-mi3v5kh1h12fcobq-016WPE3Ub3X2XqSbnakPSAvu`

### What to COMMIT ✅

**Always commit**:
- Source code changes (`src/*.py`)
- Configuration updates (`config/*.yml`)
- Documentation (`*.md` files)
- Scripts (`*.sh`, `*.bat`, `*.ps1`)
- Tests (`tests/*.py`)
- GitHub Actions (`.github/workflows/*.yml`)
- Dependencies (`requirements.txt`)

### What NOT to COMMIT ❌

**Never commit** (already in `.gitignore`):
- NFIRS data files (`data/*.csv`, `data/*.zip`)
- Generated reports (`reports/*`)
- Log files (`logs/*.log`)
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)

### Commit Message Format

**Good Examples**:
```bash
git commit -m "Add NFIRS codes for solid-state battery fires"
git commit -m "Fix date parsing for international NFIRS data"
git commit -m "Improve vehicle fire subcategory detection"
git commit -m "Update alert thresholds based on 2024 data patterns"
```

**Pattern**: `<Verb> <what changed> [context]`

### Push Protocol

**CRITICAL**: Branch must start with `claude/` and end with session ID

```bash
# Correct
git push -u origin claude/claude-md-mi3v5kh1h12fcobq-016WPE3Ub3X2XqSbnakPSAvu

# Will fail with 403
git push -u origin feature/my-branch
```

**Retry Logic**: For network failures, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Pre-Commit Checklist

Before committing:
```bash
# Check status
git status

# Review changes
git diff

# Verify no data files staged
git diff --cached | grep -E "data/.*\.csv"

# Run tests
pytest tests/

# Verify Python syntax
python -m py_compile src/*.py
```

---

## Common Tasks

### Adding New NFIRS Codes

1. **Edit Configuration**
```bash
# Open config/nfirs_codes.yml
# Add codes under appropriate section
```

2. **Example Addition**
```yaml
equipment_codes:
  battery_equipment:
    - 919   # Existing
    - 999   # New solid-state battery code
```

3. **Test Changes**
```bash
python src/main.py check-codes --type battery
python src/main.py analyze --type battery
```

4. **Commit**
```bash
git add config/nfirs_codes.yml
git commit -m "Add NFIRS code 999 for solid-state batteries"
git push
```

### Adding New Keywords

1. **Edit Configuration**
```yaml
narrative_keywords:
  battery:
    - "lithium"
    - "thermal runaway"
    - "solid-state battery"  # New keyword
```

2. **Test**
```bash
python src/main.py analyze --type battery
# Check if new keyword matches incidents
```

### Modifying Alert Thresholds

1. **Edit Configuration**
```yaml
# config/workflow_config.yml
alerts:
  incidents_per_month: 15  # Changed from 10
  property_loss_threshold: 2000000  # Changed from 1M
```

2. **Document Changes**
```bash
git commit -m "Update alert thresholds for 2025 monitoring season"
```

### Adding New Analysis Method

1. **Implement in `src/analyzers.py`**
```python
class NFIRSAnalyzer:
    def my_new_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        New analysis method.

        Args:
            df: Incident data

        Returns:
            Analysis results
        """
        results = {}
        # Implementation
        return results
```

2. **Add to Summary Report**
```python
def generate_summary_report(self, df):
    summary = {
        'temporal': self.temporal_analysis(df),
        'geographic': self.geographic_analysis(df),
        'my_new': self.my_new_analysis(df),  # Add here
    }
    return summary
```

3. **Update Reporter**
```python
# src/reporters.py
# Add visualization or section for new analysis
```

4. **Test and Commit**
```bash
pytest tests/
git add src/analyzers.py src/reporters.py
git commit -m "Add new analysis method for equipment failure patterns"
```

### Debugging Issues

**Enable Debug Logging**:
```bash
python src/main.py --log-level DEBUG analyze --type all
```

**Check Log File**:
```bash
tail -f logs/nfirs_workflow.log
```

**Test with Sample Data**:
```bash
python src/main.py create-sample
python src/main.py analyze --type all
```

---

## AI Assistant Guidelines

### When Working on This Repository

1. **ALWAYS Read Existing Documentation First**
   - Check `README.md`, `USAGE.md`, `PROJECT_SUMMARY.md`
   - Review `GIT_WORKFLOW.md` for commit guidelines
   - Understand the codebase structure before making changes

2. **Follow Established Patterns**
   - Use existing code as a template for new features
   - Match naming conventions (snake_case for functions, PascalCase for classes)
   - Include type hints and docstrings
   - Add logging statements for important operations

3. **Configuration Over Code**
   - Add new NFIRS codes to `config/nfirs_codes.yml`, not hardcoded
   - Adjust thresholds in `config/workflow_config.yml`, not in source
   - Keep configuration separate from implementation

4. **Testing is Mandatory**
   - Test changes with sample data: `python src/main.py create-sample`
   - Run unit tests: `pytest tests/`
   - Verify output reports are generated correctly

5. **Git Hygiene**
   - NEVER commit data files (CSV, ZIP)
   - NEVER commit generated reports
   - ALWAYS check `git status` and `git diff` before committing
   - Use descriptive commit messages

6. **Documentation**
   - Update relevant `.md` files when adding features
   - Add inline comments for complex logic
   - Update YAML comments when adding new codes
   - Keep `CLAUDE.md` updated with architectural changes

### Common AI Assistant Mistakes to Avoid

❌ **Don't**: Hardcode NFIRS codes in Python files
✅ **Do**: Add them to `config/nfirs_codes.yml`

❌ **Don't**: Commit sample data or test reports
✅ **Do**: Ensure `.gitignore` is respected

❌ **Don't**: Skip type hints and docstrings
✅ **Do**: Follow existing code style meticulously

❌ **Don't**: Make breaking changes without discussion
✅ **Do**: Extend functionality while maintaining backward compatibility

❌ **Don't**: Ignore errors silently
✅ **Do**: Add proper logging and error handling

### Suggested Workflow for AI Assistants

1. **Understand the Request**
   - What is the user asking for?
   - Is it a bug fix, feature addition, or analysis question?

2. **Review Relevant Code**
   - Read the specific module involved
   - Check existing tests
   - Review configuration files

3. **Plan the Change**
   - Identify what needs to be modified
   - Consider impact on other components
   - Determine if tests need updates

4. **Implement**
   - Make minimal, focused changes
   - Follow existing code patterns
   - Add appropriate logging

5. **Test**
   - Run relevant unit tests
   - Test with sample data
   - Verify output is correct

6. **Document**
   - Update docstrings
   - Update `.md` files if needed
   - Add configuration comments

7. **Commit**
   - Check what changed: `git status`, `git diff`
   - Stage only relevant files
   - Write clear commit message
   - Push to correct branch

### Understanding User Intent

**Questions about codebase** → Read and explain from existing code/docs
**Bug reports** → Investigate, fix, test, commit
**Feature requests** → Plan, implement, test, document, commit
**Data analysis** → Run analysis commands, interpret results
**Configuration help** → Explain YAML files, suggest changes
**Performance issues** → Review `FIX_SLOW_ANALYSIS.md`, suggest optimizations

---

## Quick Reference

### File Locations

| Need | File Path |
|------|-----------|
| NFIRS codes | `config/nfirs_codes.yml` |
| Workflow settings | `config/workflow_config.yml` |
| Data loading | `src/data_loader.py` |
| Filtering logic | `src/filters.py` |
| Analysis methods | `src/analyzers.py` |
| Report generation | `src/reporters.py` |
| CLI interface | `src/main.py` |
| Unit tests | `tests/test_filters.py` |
| GitHub Actions | `.github/workflows/nfirs_analysis.yml` |

### Common Commands

```bash
# Setup
pip install -r requirements.txt

# Generate test data
python src/main.py create-sample

# Run analysis
python src/main.py analyze --type all

# Run tests
pytest tests/

# Check codes
python src/main.py check-codes --type all

# View stats
python src/main.py stats --input data/basicincident.csv

# Git workflow
git status
git diff
git add src/ config/
git commit -m "Description of changes"
git push -u origin <branch-name>
```

### Key NFIRS Codes

| Type | Code | Description |
|------|------|-------------|
| Equipment | 262 | Solar energy system |
| Equipment | 919 | Battery (general) |
| Equipment | 126 | Battery charger |
| Heat Source | 87 | Solar energy collection system |
| Heat Source | 82 | Battery |
| Incident | 111 | Building fire |
| Incident | 131 | Passenger vehicle fire |

### Dependencies

```
pandas, numpy, pyyaml, click          # Core
matplotlib, seaborn, plotly           # Visualization
geopandas                             # Geographic analysis
jinja2                                # HTML templates
openpyxl                              # Excel export
python-dotenv, requests               # Utilities
```

---

## Version History

- **v1.0** (2025-11-18): Initial CLAUDE.md creation with comprehensive documentation

---

## Additional Resources

- **User Documentation**: `README.md`, `QUICKSTART.md`, `USAGE.md`
- **Git Guidelines**: `GIT_WORKFLOW.md`
- **Project Details**: `PROJECT_SUMMARY.md`
- **NFIRS Reference**: [NFIRS Complete Reference Guide](https://www.usfa.fema.gov/downloads/pdf/nfirs/NFIRS_Complete_Reference_Guide_2015.pdf)
- **FEMA Data**: [OpenFEMA Data Sets](https://www.fema.gov/about/openfema/data-sets)

---

**Remember**: This is a production system used for fire safety analysis. Changes should be careful, tested, and documented. When in doubt, preserve existing functionality and extend conservatively.
