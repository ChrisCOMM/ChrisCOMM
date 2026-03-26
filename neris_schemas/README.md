# NERIS Schema Files

This directory contains schema files from the NERIS (National Emergency Response Information System) framework.

**Source:** https://github.com/ulfsri/neris-framework
**Downloaded:** March 26, 2026
**Version:** Beta release (May 2024)

---

## Directory Structure

```
neris_schemas/
├── README.md                           # This file
├── NERIS_README.md                     # Official NERIS framework README
├── modules/                            # NERIS module schemas
│   ├── core_mod_incident.yml          # Core incident module (replaces NFIRS Basic)
│   ├── mod_fire.yml                   # Fire module (replaces NFIRS Fire)
│   └── mod_battery_incident.yml       # Battery incident module (NEW!)
└── value_sets/                        # NERIS value set schemas (code lists)
    ├── type_incident.yml              # Incident type codes
    ├── type_emerghaz_elec.yml         # Electrical emerging hazards (batteries, EVs)
    ├── type_emerghaz_pv.yml           # Photovoltaic (solar) hazard types
    └── type_emerghaz_pv_ign.yml       # PV ignition classification
```

---

## Module Files

### `core_mod_incident.yml`
**Purpose:** Core incident data module (replaces NFIRS Basic Module)

**Key Fields:**
- `incident_neris_id` - Unique NERIS identifier
- `incident_internal_id` - Department's internal incident ID
- `incident_final_type` - Hierarchical incident type classification
- `incident_special_modifier` - Incident magnitude/class modifiers
- Module references: fire, hazard, medical, rescue, etc.

### `mod_fire.yml`
**Purpose:** Fire incident data (replaces NFIRS Fire Module)

**Key Fields:**
- Fire suppression information
- Structure fire details (arrival conditions, damage, floor/room of origin)
- Transportation fire details
- Outside fire details
- Investigation need and type

### `mod_battery_incident.yml` 🆕
**Purpose:** Dedicated battery incident analysis module

**THIS IS NEW!** NFIRS had no equivalent. This module provides:

**Product Information:**
- `product_type` - Battery product category
- `original_battery` - Original vs. aftermarket
- `safety_listed` - UL or other certification
- `vehicle_battery` - EV battery flag

**Battery Specifications:**
- `battery_cell` - Cell type
- `battery_chemistry` - Chemistry type (Li-ion, LiFePO4, etc.)
- `battery_size_voltage` - Voltage rating
- `battery_size_amp_hour` - Amp-hour capacity
- `battery_size_watt_hour` - Watt-hour capacity
- `battery_charge` - State of charge at incident (%)

**Incident Details:**
- `thermal_runaway` - Thermal runaway indicator ⚠️
- `charging_at_ignition` - Was battery charging?
- `installation_status` - Permanently installed?
- `incident_indoor_outdoor` - Indoor vs. outdoor
- `in_direct_sunlight` - Direct sunlight exposure
- `impacted_from_source` - Impacted by another ignition source?

**Suppression:**
- `fd_suppression` - Suppression methods used

---

## Value Set Files

### `type_incident.yml`
**Purpose:** Incident type code definitions

**Structure:** Three-level hierarchy
```yaml
'FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE':
  value_1: FIRE
  value_2: STRUCTURE_FIRE
  value_3: ROOM_AND_CONTENTS_FIRE
  NFIRS Crosswalk: 111, 112, 113, 114, 115, 116, 117, 118, 121, 122, 123, 120
```

### `type_emerghaz_elec.yml`
**Purpose:** Electrical emerging hazard codes (batteries, EVs, e-mobility)

**Categories:**
- `CONSUMER_PRODUCTS` - Phones, tablets, e-cigarettes, power banks
- `E_MOBILITY` - E-bikes, e-scooters, mobility devices
- `ENERGY_STORAGE_SYSTEM` - Battery ESS/BESS systems
- `ELECTRIC_VEHICLE` - EVs, hybrids, plug-in hybrids

**Example Codes:**
```yaml
'E_MOBILITY: POWER_ASSISTED_BICYCLE':
  value_1: E_MOBILITY
  value_2: POWER_ASSISTED_BICYCLE
  description_1: Power Assisted Bicycle
  description_2: E-Mobility

'ELECTRIC_VEHICLE: CAR_RR: FULL_ELECTRIC':
  value_1: ELECTRIC_VEHICLE
  value_2: CAR_RR
  value_3: FULL_ELECTRIC
  description: Road Registered Car - Full Electric
```

### `type_emerghaz_pv.yml`
**Purpose:** Photovoltaic (solar) system type codes

**Codes:**
- `PANEL_WATER_HEATING` - Solar water heating panels
- `PANEL_POWER_GENERATION` - Standard solar panels
- `TILE_POWER_GENERATION` - Solar tile systems
- `THIN_FILM_POWER_GENERATION` - Thin-film PV systems

### `type_emerghaz_pv_ign.yml`
**Purpose:** PV ignition source classification

**Codes:**
- `SOURCE` - PV system was ignition source
- `TARGET` - PV system was target of fire from another source

---

## Usage in ChrisCOMM Project

These schema files are used to:

1. **Understand NERIS data structure** for migration planning
2. **Map NFIRS codes to NERIS codes** for backward compatibility
3. **Reference field definitions** during code development
4. **Validate data** against NERIS schema requirements

**See Documentation:**
- `docs/NERIS_SCHEMA_ANALYSIS.md` - Comprehensive schema analysis and migration guide
- `docs/NERIS_CODE_REFERENCE.md` - Quick reference for solar and battery codes
- `docs/NERIS_FINDINGS_SUMMARY.md` - Executive summary of NERIS analysis

---

## Related Resources

- **NERIS GitHub:** https://github.com/ulfsri/neris-framework
- **NERIS Wiki:** https://github.com/ulfsri/neris-framework/wiki
- **NERIS API (Production):** https://api.neris.fsri.org/v1/docs
- **NERIS API (Test):** https://api-test.neris.fsri.org/v1/docs
- **NERIS Helpdesk:** https://neris.atlassian.net/servicedesk/customer/portals
- **NERIS Discussions:** https://github.com/ulfsri/neris-framework/discussions
- **NERIS Website:** https://neris.fsri.org/technical-reference

---

## Updates

To update these schemas to the latest version:

```bash
# Clone/update the NERIS framework repository
git clone https://github.com/ulfsri/neris-framework.git /tmp/neris-framework

# Copy updated core module schemas
cp /tmp/neris-framework/core_schemas/modules/yml/incident/core_mod_incident.yml neris_schemas/modules/
cp /tmp/neris-framework/core_schemas/modules/yml/incident/mod_fire.yml neris_schemas/modules/
cp /tmp/neris-framework/secondary_schemas/modules/yml/incident_analysis/mod_battery_incident.yml neris_schemas/modules/

# Copy updated value set schemas
cp /tmp/neris-framework/core_schemas/value_sets/yml/type_incident.yml neris_schemas/value_sets/
cp /tmp/neris-framework/core_schemas/value_sets/yml/type_emerghaz_elec.yml neris_schemas/value_sets/
cp /tmp/neris-framework/core_schemas/value_sets/yml/type_emerghaz_pv.yml neris_schemas/value_sets/
cp /tmp/neris-framework/core_schemas/value_sets/yml/type_emerghaz_pv_ign.yml neris_schemas/value_sets/

# Update the NERIS README
cp /tmp/neris-framework/README.md neris_schemas/NERIS_README.md
```

---

**Last Updated:** March 26, 2026
**NERIS Framework Version:** Beta (May 2024)
