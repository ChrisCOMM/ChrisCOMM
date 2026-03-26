# NERIS Schema Analysis & Migration Guide

**Date:** March 26, 2026
**Analysis Version:** 1.0
**NERIS Framework Version:** Beta (as of May 2024)

---

## Executive Summary

This document provides a comprehensive analysis of the NERIS (National Emergency Response Information System) data schemas and their mapping to the NFIRS (National Fire Incident Reporting System) fields currently used in the ChrisCOMM project.

### Critical Timeline
- **NFIRS Sunset Date:** February 2026 (10 months away)
- **NERIS Status:** Beta release (May 2024), Production API available
- **Migration Urgency:** HIGH - This project must transition to NERIS before NFIRS sunsets

---

## Table of Contents

1. [NERIS vs NFIRS Overview](#neris-vs-nfirs-overview)
2. [Key Differences](#key-differences)
3. [Schema Structure](#schema-structure)
4. [Incident Type Mapping](#incident-type-mapping)
5. [Solar Panel Fire Support](#solar-panel-fire-support)
6. [Lithium-Ion Battery Fire Support](#lithium-ion-battery-fire-support)
7. [Field Mapping Table](#field-mapping-table)
8. [Migration Recommendations](#migration-recommendations)
9. [API Access](#api-access)

---

## NERIS vs NFIRS Overview

### NFIRS (Legacy System - Sunsets Feb 2026)
- **Format:** CSV files with comma (`,`) delimiter
- **Structure:** Separate modules (Basic, Fire, Structure, Wildland, Hazmat)
- **Field Names:** Abbreviated uppercase (e.g., `HEAT_SOURC`, `FIRST_IGN`)
- **Codes:** Numeric codes (e.g., `111` = Building fire, `82` = Battery heat source)
- **Access:** File-based downloads from FEMA OpenFEMA

### NERIS (Current System - Production)
- **Format:** CSV files with caret (`^`) delimiter, YML, XLSX, API
- **Structure:** Hierarchical modules with nested relationships
- **Field Names:** Descriptive lowercase (e.g., `heat_source`, `item_first_ig`)
- **Codes:** Hierarchical text codes (e.g., `FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE`)
- **Access:** API-based (OpenAPI/Swagger) + file downloads
- **New Features:**
  - Dedicated battery incident module (`mod_battery_incident`)
  - Emerging hazard tracking (solar PV, batteries, e-mobility)
  - Enhanced metadata and computed fields

---

## Key Differences

### 1. File Format
```
NFIRS:  field1,field2,field3
NERIS:  field1^field2^field3
```

### 2. Column Naming
| NFIRS Column | NERIS Column | Description |
|--------------|--------------|-------------|
| `HEAT_SOURC` | `heat_source` | Heat source |
| `FIRST_IGN` | `item_first_ig` | First item ignited |
| `AREA_ORIG` | `area_origin` | Area of origin |
| `INC_TYPE` | `incident_final_type` | Incident type |

### 3. Incident Type Structure

**NFIRS:** Single numeric code
```
111 = Building fire
131 = Passenger vehicle fire
```

**NERIS:** Hierarchical three-level structure
```
value_1: FIRE
value_2: STRUCTURE_FIRE
value_3: ROOM_AND_CONTENTS_FIRE
```

### 4. NFIRS Crosswalk
NERIS provides explicit mapping to NFIRS codes:
```yaml
'FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE':
  value_1: FIRE
  value_2: STRUCTURE_FIRE
  value_3: ROOM_AND_CONTENTS_FIRE
  NFIRS Crosswalk: 111, 112, 113, 114, 115, 116, 117, 118, 121, 122, 123, 120
```

---

## Schema Structure

### Core Schemas (Required for all incidents)

1. **`core_mod_incident.yml`** - Replaces NFIRS Basic Module
   - Incident identifiers
   - Incident type
   - Location information
   - Timestamps
   - References to other modules (fire, hazard, medical, rescue)

2. **`core_mod_dispatch.yml`** - CAD/Dispatch Data
   - Call information
   - Unit response data
   - Dispatch codes

3. **`core_mod_entity_fd.yml`** - Fire Department Information
   - Department identifiers
   - Jurisdiction data

### Fire Module (Conditional - for fire incidents)

4. **`mod_fire.yml`** - Replaces NFIRS Fire Module
   - Fire suppression information
   - Structure fire details
   - Transportation fire details
   - Outside fire details
   - Investigation information

### Secondary Schemas (Analysis/Specialized)

5. **`mod_battery_incident.yml`** - NEW! Dedicated Battery Incident Module
   - Product type classification
   - Battery specifications (chemistry, voltage, capacity)
   - Thermal runaway indicators
   - Charging status at ignition
   - Safety listing information
   - Vehicle battery flag
   - EV-specific data

6. **Solar/PV Support** - Integrated into emerging hazards
   - PV system type classification
   - Ignition source tracking

---

## Incident Type Mapping

### Building/Structure Fires

| NFIRS Code | NFIRS Description | NERIS Type |
|------------|-------------------|------------|
| 111 | Building fire | `FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE` |
| 112 | Fires in structure other than building | `FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE` |
| 113 | Cooking fire, confined to container | `FIRE: STRUCTURE_FIRE: CONFINED_COOKING_APPLIANCE_FIRE` |
| 118 | Trash or rubbish fire, contained | `FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE` |

### Vehicle/Transportation Fires

| NFIRS Code | NFIRS Description | NERIS Type |
|------------|-------------------|------------|
| 130 | Mobile property (vehicle) fire, other | `FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_PASSENGER` |
| 131 | Passenger vehicle fire | `FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_PASSENGER` |
| 132 | Road freight or transport vehicle fire | `FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_COMMERCIAL` |
| 138 | Off-road vehicle or heavy equipment fire | `FIRE: TRANSPORTATION_FIRE: POWERED_MOBILITY_DEVICE_FIRE` |

### Vegetation/Outside Fires

| NFIRS Code | NFIRS Description | NERIS Type |
|------------|-------------------|------------|
| 140 | Natural vegetation fire, other | `FIRE: OUTSIDE_FIRE: VEGETATION_GRASS_FIRE` |
| 141 | Forest, woods or wildland fire | `FIRE: OUTSIDE_FIRE: WILDFIRE_WILDLAND` |
| 142 | Brush or brush-and-grass mixture fire | `FIRE: OUTSIDE_FIRE: VEGETATION_GRASS_FIRE` |
| 143 | Grass fire | `FIRE: OUTSIDE_FIRE: VEGETATION_GRASS_FIRE` |

---

## Solar Panel Fire Support

### NFIRS Codes (Current Project Uses)
```yaml
equipment_codes:
  solar_equipment:
    - 262   # Solar energy system
    - 261   # Fixed wiring and related equipment
    - 132   # Transformer

heat_sources:
  - 87    # Solar energy collection system
```

### NERIS Equivalents

#### Type: Emerging Hazard - Photovoltaic (PV)
Location: `type_emerghaz_pv.yml`

```yaml
PANEL_WATER_HEATING:
  description: Panel Water Heating

PANEL_POWER_GENERATION:
  description: Panel Power Generation

TILE_POWER_GENERATION:
  description: Tile Power Generation

THIN_FILM_POWER_GENERATION:
  description: Thin Film Power Generation
```

#### PV Ignition Classification
Location: `type_emerghaz_pv_ign.yml`

```yaml
SOURCE:
  description: PV system was ignition source

TARGET:
  description: PV system was target of fire from another source
```

### Solar Fire Detection Strategy

**NFIRS Method (Current):**
```python
# Filter by equipment code OR heat source OR narrative keywords
equipment_codes: [262, 261, 132]
heat_sources: [87]
keywords: ["solar panel", "photovoltaic", "PV system", "inverter"]
```

**NERIS Method (Recommended):**
```python
# Use emerging hazard classification
incident_type: FIRE
emerging_hazard_type: type_emerghaz_pv
pv_types: [PANEL_POWER_GENERATION, TILE_POWER_GENERATION, THIN_FILM_POWER_GENERATION]
pv_ignition: SOURCE
```

---

## Lithium-Ion Battery Fire Support

### NFIRS Codes (Current Project Uses)
```yaml
equipment_codes:
  battery_equipment:
    - 919   # Battery (general)
    - 126   # Battery charger
    - 125   # Rechargeable battery

heat_sources:
  - 82    # Battery
```

### NERIS Equivalents

#### Dedicated Battery Incident Module
Location: `mod_battery_incident.yml`

**This is a major enhancement!** NERIS has a comprehensive battery-specific module with detailed fields:

```yaml
# Product Information
product_type: Array[Text]  # From type_emerghaz_elec
original_battery: Boolean
safety_listed: Boolean
vehicle_battery: Boolean   # Triggers mod_transportation_fire

# Battery Specifications
battery_cell: type_battery_cell
battery_chemistry: type_battery_chemistry
battery_size_voltage: Integer
battery_size_amp_hour: Integer
battery_size_watt_hour: Integer
battery_charge: Integer (percentage)

# Incident Details
charging_at_ignition: Boolean
thermal_runaway: Boolean
impacted_from_source: Boolean
installation_status: Boolean
incident_indoor_outdoor: type_indoor_outdoor
in_direct_sunlight: Boolean

# Suppression
fd_suppression: Array[Text]
```

#### Type: Emerging Hazard - Electric
Location: `type_emerghaz_elec.yml`

**Consumer Products (Battery-Powered)**
```yaml
CONSUMER_PRODUCTS: CELL_PHONE
CONSUMER_PRODUCTS: COMPUTER_TABLET
CONSUMER_PRODUCTS: ELECTRONIC_CIGARETTE
CONSUMER_PRODUCTS: POWER_BANK
CONSUMER_PRODUCTS: APPLIANCE_TOOL
CONSUMER_PRODUCTS: TOY
```

**E-Mobility (E-bikes, E-scooters)**
```yaml
E_MOBILITY: POWER_ASSISTED_BICYCLE
  description: Power Assisted Bicycle (E-bike)

E_MOBILITY: ELECTRIC_SCOOTER_MOPED
  description: Electric Scooter/Moped (E-scooter)

E_MOBILITY: PERSONAL_MOBILITY_ASSIST
  description: Personal Mobility Assist
```

**Energy Storage Systems (ESS/BESS)**
```yaml
ENERGY_STORAGE_SYSTEM: BATTERY
  description: Battery (Electro-Chemical)

ENERGY_STORAGE_SYSTEM: HYDROELECTRIC
  description: Pumped-Storage Hydroelectric
```

**Electric Vehicles**
```yaml
ELECTRIC_VEHICLE: CAR_RR: FULL_ELECTRIC
  description: Road Registered Car - Full Electric

ELECTRIC_VEHICLE: CAR_RR: PLUG_IN_HYBRID
  description: Road Registered Car - Plug-In Hybrid

ELECTRIC_VEHICLE: CAR_RR: HYBRID
  description: Road Registered Car - Hybrid

ELECTRIC_VEHICLE: TRUCK_PASSENGER_RR: FULL_ELECTRIC
  description: Road Registered Passenger Truck - Full Electric
```

### Battery Fire Detection Strategy

**NFIRS Method (Current):**
```python
# Filter by equipment code OR heat source OR narrative keywords
equipment_codes: [919, 126, 125]
heat_sources: [82]
keywords: ["lithium", "li-ion", "battery", "EV", "e-bike", "ESS", "BESS", "thermal runaway"]
```

**NERIS Method (Recommended):**
```python
# Use dedicated battery module + emerging hazard classification
has_battery_module: True
emerging_hazard_type: type_emerghaz_elec
product_categories: [
    CONSUMER_PRODUCTS,
    E_MOBILITY,
    ENERGY_STORAGE_SYSTEM,
    ELECTRIC_VEHICLE
]
thermal_runaway: True  # Optional: thermal runaway indicator
```

---

## Field Mapping Table

### Core Incident Fields

| NFIRS Field | NERIS Field | Type | Notes |
|-------------|-------------|------|-------|
| `STATE` | `state` | Text | State abbreviation |
| `FDID` | Embedded in `incident_neris_id` | Text | Fire department ID |
| `INC_DATE` | Computed from `incident_neris_id` | Timestamp | Incident date/time |
| `INC_NO` | `incident_internal_id` | Text | Department's internal ID |
| `EXP_NO` | Exposure tracking in `mod_exposure` | Integer | Exposure number |
| `INC_TYPE` | `incident_final_type` | Array | Hierarchical type |
| `AID` | `incident_aid_type` | Text | Mutual aid indicator |

### Fire Module Fields

| NFIRS Field | NERIS Field | Type | Notes |
|-------------|-------------|------|-------|
| `HEAT_SOURC` | N/A - Use emerging hazard types | - | See `type_emerghaz_*` |
| `FIRST_IGN` | Mapped to cause fields | Text | Integrated into cause classification |
| `AREA_ORIG` | `structure_room_of_origin` | Text | For structure fires |
| `NUM_UNIT` | Unit response in shared modules | Integer | Dispatch/response data |
| `DETECTOR_TYPE` | `structure_alarm_type` | Text | Alarm/detector classification |

### New NERIS Fields (No NFIRS Equivalent)

| NERIS Field | Type | Purpose |
|-------------|------|---------|
| `incident_neris_id` | Text | Unique NERIS identifier (FD ID + epoch timestamp) |
| `incident_special_modifier` | Array | Incident magnitude/class modifiers |
| `thermal_runaway` | Boolean | Battery thermal runaway indicator |
| `battery_chemistry` | Text | Specific battery chemistry type |
| `pv_ignition_type` | Text | SOURCE vs TARGET for PV fires |
| `computed` fields | Various | Auto-populated by NERIS system |

---

## Migration Recommendations

### Phase 1: Data Loader Updates (Week 1-2)

**Current Status:** ✅ Partial support exists
- Current code already handles `^` delimiter
- Has 3 column name mappings

**Needed Updates:**
1. Add complete column mapping dictionary
2. Implement hierarchical incident type parser
3. Add support for NERIS API data ingestion
4. Create backward compatibility mode

**Code Changes:**
```python
# src/data_loader.py

NERIS_COLUMN_MAPPING = {
    # Current mappings
    'heat_sourc': 'heat_source',
    'first_ign': 'item_first_ig',
    'area_orig': 'area_origin',

    # Add additional mappings
    'inc_type': 'incident_final_type',
    'inc_no': 'incident_internal_id',
    # ... (see full mapping table above)
}

def parse_neris_incident_type(incident_type_array):
    """Parse NERIS hierarchical incident type to NFIRS-compatible format"""
    # incident_type_array = [['FIRE', 'STRUCTURE_FIRE', 'ROOM_AND_CONTENTS_FIRE']]
    # Extract value_1, value_2, value_3
    # Map to NFIRS codes using crosswalk
    pass

def load_from_neris_api(endpoint, params):
    """Load data from NERIS API"""
    # Implement API data fetching
    pass
```

### Phase 2: Filter Updates (Week 3)

**Update `src/filters.py`:**

```python
class NERISIncidentFilter:
    """Filter for NERIS data format"""

    def filter_solar_incidents(self, df):
        """
        Filter solar panel incidents using NERIS schema
        """
        # Check emerging_hazard_type field
        solar_mask = df['emerging_hazard_type'].isin([
            'PANEL_POWER_GENERATION',
            'TILE_POWER_GENERATION',
            'THIN_FILM_POWER_GENERATION'
        ])

        # Check if PV was ignition source
        source_mask = df['pv_ignition_type'] == 'SOURCE'

        # Combine with narrative keyword matching
        return df[solar_mask & source_mask]

    def filter_battery_incidents(self, df):
        """
        Filter lithium-ion battery incidents using NERIS schema
        """
        # Check if battery module is present
        has_battery_module = ~df['battery_incident_module'].isna()

        # Check emerging hazard types
        battery_hazard = df['emerging_hazard_type'].str.contains(
            'BATTERY|E_MOBILITY|ELECTRIC_VEHICLE|ENERGY_STORAGE',
            case=False, na=False
        )

        # Optional: Filter for thermal runaway events
        thermal_runaway = df['thermal_runaway'] == True

        return df[has_battery_module | battery_hazard]
```

### Phase 3: Configuration Updates (Week 3-4)

**Update `config/workflow_config.yml`:**

```yaml
# Data Source Settings
data_sources:
  # NERIS API configuration
  use_neris_api: true
  neris_api_endpoint: "https://api.neris.fsri.org/v1"
  neris_api_key: ${NERIS_API_KEY}  # Environment variable

  # File-based NERIS data (alternative to API)
  neris_incident_data: "data/neris_incidents.csv"
  neris_dispatch_data: "data/neris_dispatch.csv"

  # Legacy NFIRS support (for historical data)
  legacy_mode: false
  nfirs_basic_module: "data/basicincident.csv"
  nfirs_fire_module: "data/fireincident.csv"
```

**Create `config/neris_codes.yml`:**

```yaml
# NERIS Code Mappings for Solar Panel and Lithium-Ion Battery Fires

# Incident Types (Hierarchical)
incident_types:
  fire_structure:
    value_1: FIRE
    value_2: STRUCTURE_FIRE
    value_3:
      - ROOM_AND_CONTENTS_FIRE
      - CONFINED_COOKING_APPLIANCE_FIRE
    nfirs_crosswalk: [111, 112, 113, 114, 115, 116, 117, 118]

  fire_transportation:
    value_1: FIRE
    value_2: TRANSPORTATION_FIRE
    value_3:
      - VEHICLE_FIRE_PASSENGER
      - VEHICLE_FIRE_COMMERCIAL
      - POWERED_MOBILITY_DEVICE_FIRE
    nfirs_crosswalk: [130, 131, 132, 138]

  fire_outside:
    value_1: FIRE
    value_2: OUTSIDE_FIRE
    value_3:
      - VEGETATION_GRASS_FIRE
      - WILDFIRE_WILDLAND
    nfirs_crosswalk: [140, 141, 142, 143]

# Emerging Hazard Types - Solar/PV
solar_pv_types:
  - PANEL_POWER_GENERATION
  - TILE_POWER_GENERATION
  - THIN_FILM_POWER_GENERATION

pv_ignition_classification:
  source: SOURCE      # PV was ignition source
  target: TARGET      # PV was target of fire

# Emerging Hazard Types - Batteries
battery_product_types:
  consumer_products:
    - CONSUMER_PRODUCTS: CELL_PHONE
    - CONSUMER_PRODUCTS: COMPUTER_TABLET
    - CONSUMER_PRODUCTS: ELECTRONIC_CIGARETTE
    - CONSUMER_PRODUCTS: POWER_BANK
    - CONSUMER_PRODUCTS: APPLIANCE_TOOL

  e_mobility:
    - E_MOBILITY: POWER_ASSISTED_BICYCLE
    - E_MOBILITY: ELECTRIC_SCOOTER_MOPED
    - E_MOBILITY: PERSONAL_MOBILITY_ASSIST

  energy_storage:
    - ENERGY_STORAGE_SYSTEM: BATTERY

  electric_vehicles:
    - ELECTRIC_VEHICLE: CAR_RR: FULL_ELECTRIC
    - ELECTRIC_VEHICLE: CAR_RR: PLUG_IN_HYBRID
    - ELECTRIC_VEHICLE: CAR_RR: HYBRID
    - ELECTRIC_VEHICLE: TRUCK_PASSENGER_RR: FULL_ELECTRIC

# Battery Module Fields (for detailed analysis)
battery_fields:
  required:
    - product_type
    - thermal_runaway
    - charging_at_ignition

  optional:
    - battery_chemistry
    - battery_cell
    - battery_charge
    - safety_listed
    - original_battery

# Search Keywords for Narrative Text (backward compatibility)
narrative_keywords:
  solar:
    - "solar panel"
    - "photovoltaic"
    - "PV system"
    - "solar array"
    - "inverter"

  battery:
    - "lithium"
    - "li-ion"
    - "battery fire"
    - "thermal runaway"
    - "e-bike"
    - "e-scooter"
    - "EV"
    - "energy storage"
```

### Phase 4: Testing & Validation (Week 5)

1. **Download NERIS sample data** from API or test environment
2. **Run analysis pipeline** with NERIS data
3. **Compare results** with historical NFIRS data
4. **Validate incident counts** match expected patterns
5. **Test backward compatibility** with existing NFIRS data

### Phase 5: Documentation & Deployment (Week 6)

1. Update README.md with NERIS transition
2. Create NERIS_MIGRATION.md user guide
3. Update GitHub Actions workflow for NERIS API
4. Add NERIS API credentials to secrets
5. Deploy updated code

---

## API Access

### Production API
- **Swagger:** https://api.neris.fsri.org/v1/docs
- **Redoc:** https://api.neris.fsri.org/v1/redoc
- **OpenAPI Spec:** Available at `/openapi.json`

### Test Environment
- **Swagger:** https://api-test.neris.fsri.org/v1/docs
- **Redoc:** https://api-test.neris.fsri.org/v1/redoc

### Authentication
- Contact USFA/FSRI for API access credentials
- Environment variable: `NERIS_API_KEY`

### Example API Usage (Python)

```python
import requests

NERIS_API_URL = "https://api.neris.fsri.org/v1"
API_KEY = os.environ.get("NERIS_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Query incidents
params = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "incident_type": "FIRE",
    "has_battery_module": True
}

response = requests.get(
    f"{NERIS_API_URL}/incidents",
    headers=headers,
    params=params
)

incidents = response.json()
```

---

## Additional Resources

- **NERIS GitHub:** https://github.com/ulfsri/neris-framework
- **NERIS Wiki:** https://github.com/ulfsri/neris-framework/wiki
- **NERIS Helpdesk:** https://neris.atlassian.net/servicedesk/customer/portals
- **NERIS Discussions:** https://github.com/ulfsri/neris-framework/discussions
- **NERIS Website:** https://neris.fsri.org/technical-reference

---

## Conclusion

NERIS provides significant enhancements over NFIRS, particularly for tracking:
- **Battery incidents** with dedicated module and detailed fields
- **Solar/PV systems** with emerging hazard classification
- **E-mobility devices** (e-bikes, e-scooters) with specific categories
- **Electric vehicles** with detailed sub-classifications

The transition from NFIRS to NERIS will require:
1. ✅ **Data format changes** (delimiter, column names) - *Partially implemented*
2. ❌ **Filter logic updates** to use new hierarchical codes
3. ❌ **Configuration updates** for new field structures
4. ❌ **API integration** for real-time data access
5. ❌ **Testing with NERIS data** to validate migration

**Estimated Migration Time:** 6 weeks (full-time development)
**Risk Level:** Medium (NERIS is production-ready, good documentation available)
**Benefit:** Future-proof system with enhanced battery and solar fire tracking capabilities
