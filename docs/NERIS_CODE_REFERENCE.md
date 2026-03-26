# NERIS Code Quick Reference

**For ChrisCOMM Project: Solar Panel & Lithium-Ion Battery Fire Analysis**

---

## Solar Panel / Photovoltaic (PV) Codes

### Incident Classification
Use emerging hazard type: `type_emerghaz_pv`

| NERIS Code | Description | NFIRS Equivalent |
|------------|-------------|------------------|
| `PANEL_POWER_GENERATION` | Solar Panel Power Generation | Equipment code 262 |
| `TILE_POWER_GENERATION` | Solar Tile Power Generation | Equipment code 262 |
| `THIN_FILM_POWER_GENERATION` | Thin Film PV | Equipment code 262 |

### PV Ignition Source
Use: `type_emerghaz_pv_ign`

| Code | Meaning | Use Case |
|------|---------|----------|
| `SOURCE` | PV system was ignition source | Fire started in/by PV system |
| `TARGET` | PV system was target of fire | Fire spread to PV system |

### Detection Strategy
```python
# NERIS method
emerging_hazard_type in ['PANEL_POWER_GENERATION', 'TILE_POWER_GENERATION', 'THIN_FILM_POWER_GENERATION']
AND pv_ignition_type == 'SOURCE'

# Legacy NFIRS method (for historical data)
equipment_code in [262, 261, 132]
OR heat_source == 87
OR narrative contains ["solar panel", "photovoltaic", "PV system"]
```

---

## Lithium-Ion Battery Codes

### Battery Incident Module
NERIS has a dedicated module: `mod_battery_incident`

**Key Fields:**
- `thermal_runaway`: Boolean (critical indicator)
- `battery_chemistry`: Type of battery chemistry
- `charging_at_ignition`: Was battery charging when fire started
- `vehicle_battery`: Is this an EV battery
- `safety_listed`: UL or other safety certification

### Product Types
Use emerging hazard type: `type_emerghaz_elec`

#### Consumer Products
| NERIS Code | Description | Examples |
|------------|-------------|----------|
| `CONSUMER_PRODUCTS: CELL_PHONE` | Cell Phone | Phone battery fires |
| `CONSUMER_PRODUCTS: COMPUTER_TABLET` | Computer/Tablet | Laptop, iPad fires |
| `CONSUMER_PRODUCTS: ELECTRONIC_CIGARETTE` | E-Cigarette | Vape battery fires |
| `CONSUMER_PRODUCTS: POWER_BANK` | Power Bank | Portable chargers |
| `CONSUMER_PRODUCTS: APPLIANCE_TOOL` | Appliance/Tool | Power tools, etc. |

#### E-Mobility (E-bikes, E-scooters)
| NERIS Code | Description | NFIRS Equivalent |
|------------|-------------|------------------|
| `E_MOBILITY: POWER_ASSISTED_BICYCLE` | E-Bike | Keywords: "e-bike", "electric bicycle" |
| `E_MOBILITY: ELECTRIC_SCOOTER_MOPED` | E-Scooter | Keywords: "e-scooter", "electric scooter" |
| `E_MOBILITY: PERSONAL_MOBILITY_ASSIST` | Mobility Device | Wheelchair, etc. |

#### Energy Storage Systems (ESS/BESS)
| NERIS Code | Description | NFIRS Equivalent |
|------------|-------------|------------------|
| `ENERGY_STORAGE_SYSTEM: BATTERY` | Battery ESS/BESS | Keywords: "ESS", "BESS", "energy storage" |

#### Electric Vehicles
| NERIS Code | Description | NFIRS Equivalent |
|------------|-------------|------------------|
| `ELECTRIC_VEHICLE: CAR_RR: FULL_ELECTRIC` | Full EV | Equipment 831, keywords: "EV", "Tesla" |
| `ELECTRIC_VEHICLE: CAR_RR: PLUG_IN_HYBRID` | Plug-in Hybrid | Equipment 831, keywords: "PHEV" |
| `ELECTRIC_VEHICLE: CAR_RR: HYBRID` | Hybrid | Equipment 831, keywords: "hybrid" |
| `ELECTRIC_VEHICLE: TRUCK_PASSENGER_RR: FULL_ELECTRIC` | Electric Truck | Equipment 832, keywords: "electric truck" |

### Detection Strategy
```python
# NERIS method (preferred)
has_battery_module == True
OR emerging_hazard_type starts_with ['CONSUMER_PRODUCTS', 'E_MOBILITY', 'ENERGY_STORAGE_SYSTEM', 'ELECTRIC_VEHICLE']
OR thermal_runaway == True

# Legacy NFIRS method (for historical data)
equipment_code in [919, 126, 125]
OR heat_source == 82
OR narrative contains ["lithium", "li-ion", "battery", "thermal runaway", "EV", "e-bike"]
```

---

## Incident Type Codes

### Structure Fires (Buildings with Solar/Battery)
| NERIS Hierarchical Code | NFIRS Code |
|-------------------------|------------|
| `FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE` | 111, 112 |
| `FIRE: STRUCTURE_FIRE: CONFINED_COOKING_APPLIANCE_FIRE` | 113 |

**Detection:**
```python
incident_final_type.value_1 == 'FIRE'
AND incident_final_type.value_2 == 'STRUCTURE_FIRE'
```

### Transportation Fires (EVs, E-bikes, E-scooters)
| NERIS Hierarchical Code | NFIRS Code |
|-------------------------|------------|
| `FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_PASSENGER` | 130, 131 |
| `FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_COMMERCIAL` | 132 |
| `FIRE: TRANSPORTATION_FIRE: POWERED_MOBILITY_DEVICE_FIRE` | 138 |

**Detection:**
```python
incident_final_type.value_1 == 'FIRE'
AND incident_final_type.value_2 == 'TRANSPORTATION_FIRE'
```

### Outside Fires (Solar Farms, Outdoor ESS)
| NERIS Hierarchical Code | NFIRS Code |
|-------------------------|------------|
| `FIRE: OUTSIDE_FIRE: VEGETATION_GRASS_FIRE` | 140, 142, 143 |
| `FIRE: OUTSIDE_FIRE: WILDFIRE_WILDLAND` | 141 |
| `FIRE: OUTSIDE_FIRE: UTILITY_INFRASTRUCTURE_FIRE` | Solar farm fires |

**Detection:**
```python
incident_final_type.value_1 == 'FIRE'
AND incident_final_type.value_2 == 'OUTSIDE_FIRE'
```

---

## Combined Query Examples

### All Solar Panel Fires
```python
# NERIS format
SELECT * FROM incidents
WHERE (
    emerging_hazard_type IN (
        'PANEL_POWER_GENERATION',
        'TILE_POWER_GENERATION',
        'THIN_FILM_POWER_GENERATION'
    )
    AND pv_ignition_type = 'SOURCE'
)
OR narrative LIKE '%solar panel%'
OR narrative LIKE '%photovoltaic%'
```

### All Lithium-Ion Battery Fires
```python
# NERIS format
SELECT * FROM incidents
WHERE (
    battery_incident_module IS NOT NULL
    OR thermal_runaway = TRUE
    OR emerging_hazard_type LIKE 'CONSUMER_PRODUCTS:%'
    OR emerging_hazard_type LIKE 'E_MOBILITY:%'
    OR emerging_hazard_type LIKE 'ENERGY_STORAGE_SYSTEM:%'
    OR emerging_hazard_type LIKE 'ELECTRIC_VEHICLE:%'
)
AND incident_final_type.value_1 = 'FIRE'
```

### E-Bike and E-Scooter Fires Only
```python
# NERIS format
SELECT * FROM incidents
WHERE emerging_hazard_type IN (
    'E_MOBILITY: POWER_ASSISTED_BICYCLE',
    'E_MOBILITY: ELECTRIC_SCOOTER_MOPED'
)
AND incident_final_type.value_1 = 'FIRE'
```

### EV Battery Fires
```python
# NERIS format
SELECT * FROM incidents
WHERE (
    vehicle_battery = TRUE
    OR emerging_hazard_type LIKE 'ELECTRIC_VEHICLE:%'
)
AND incident_final_type.value_2 = 'TRANSPORTATION_FIRE'
```

### Energy Storage System (ESS/BESS) Fires
```python
# NERIS format
SELECT * FROM incidents
WHERE emerging_hazard_type = 'ENERGY_STORAGE_SYSTEM: BATTERY'
AND incident_final_type.value_1 = 'FIRE'
```

---

## Key Advantages of NERIS

### For Solar Panel Tracking
✅ **Dedicated PV classification** - No longer relying on generic equipment codes
✅ **Ignition source vs. target** - Can distinguish fires caused by PV vs. fires that spread to PV
✅ **Solar farm fires** - Better tracking for large installations

### For Battery Tracking
✅ **Dedicated battery module** - Comprehensive battery-specific data collection
✅ **Thermal runaway indicator** - Direct tracking of this critical event
✅ **Battery specifications** - Chemistry, voltage, capacity tracking
✅ **Charging status** - Know if battery was charging at time of fire
✅ **Safety certification** - Track UL-listed vs. uncertified products
✅ **Granular categorization** - Separate codes for e-bikes, e-scooters, EVs, ESS, consumer products

---

## Migration Checklist

- [ ] Update data loader to handle NERIS field names
- [ ] Implement hierarchical incident type parsing
- [ ] Add emerging hazard type filters
- [ ] Add battery module field extraction
- [ ] Update config/neris_codes.yml
- [ ] Test with NERIS sample data
- [ ] Update documentation
- [ ] Deploy to production before Feb 2026

---

**Last Updated:** March 26, 2026
**NERIS Framework Version:** Beta
**Project:** ChrisCOMM - NFIRS to NERIS Migration
