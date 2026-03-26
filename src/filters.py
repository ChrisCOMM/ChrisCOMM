"""
NFIRS/NERIS Incident Filters Module

Filters NFIRS (legacy) and NERIS (current) data for solar panel and lithium-ion battery incidents.
Automatically detects data format and uses appropriate filtering methods.

NFIRS = National Fire Incident Reporting System (sunsets Feb 2026)
NERIS = National Emergency Response Information System (current)
"""

import pandas as pd
import yaml
import logging
import re
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NFIRSIncidentFilter:
    """
    Filters NFIRS (legacy) and NERIS (current) incidents for specific equipment types.

    Supports:
    - NFIRS format (equipment codes, heat sources, narrative keywords)
    - NERIS format (emerging hazard types, structured fields, hierarchical types)
    - Automatic format detection
    - Enhanced categorization for battery and solar incidents
    """

    def __init__(self, codes_config_path: str = "config/nfirs_codes.yml",
                 workflow_config_path: str = "config/workflow_config.yml"):
        """
        Initialize the filter with NFIRS codes.

        Args:
            codes_config_path: Path to NFIRS codes configuration
            workflow_config_path: Path to workflow configuration
        """
        self.codes = self._load_codes(codes_config_path)
        self.workflow_config = self._load_config(workflow_config_path)

        # Extract relevant code sets
        self.solar_equipment_codes = set(self.codes.get('equipment_codes', {}).get('solar_equipment', []))
        self.battery_equipment_codes = set(self.codes.get('equipment_codes', {}).get('battery_equipment', []))
        self.ev_codes = set(self.codes.get('equipment_codes', {}).get('electric_vehicle', []))
        self.solar_heat_sources = {87}  # Solar energy collection system
        self.battery_heat_sources = {82}  # Battery

        # Narrative keywords
        self.solar_keywords = self.codes.get('narrative_keywords', {}).get('solar', [])
        self.battery_keywords = self.codes.get('narrative_keywords', {}).get('battery', [])

        # Filtering settings
        filter_settings = self.workflow_config.get('filtering', {})
        self.use_narrative = filter_settings.get('use_narrative_matching', True)
        self.min_keywords = filter_settings.get('min_keyword_matches', 1)

        # Data format detection (set by filter methods)
        self.data_format = None  # Will be 'NFIRS' or 'NERIS'

        # NERIS-specific code sets (hierarchical)
        self.neris_battery_products = {
            'CONSUMER_PRODUCTS',
            'E_MOBILITY',
            'ENERGY_STORAGE_SYSTEM',
            'ELECTRIC_VEHICLE',
        }

        self.neris_pv_types = {
            'PANEL_POWER_GENERATION',
            'TILE_POWER_GENERATION',
            'THIN_FILM_POWER_GENERATION',
        }

    def _load_codes(self, path: str) -> Dict:
        """Load NFIRS codes from YAML file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Codes config file not found: {path}")
            return {}

    def _load_config(self, path: str) -> Dict:
        """Load workflow configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Workflow config file not found: {path}")
            return {}

    def _detect_format(self, df: pd.DataFrame) -> str:
        """
        Detect if data is in NFIRS or NERIS format.

        Args:
            df: DataFrame to analyze

        Returns:
            'NERIS' or 'NFIRS'
        """
        # Check for NERIS-specific columns
        neris_indicators = [
            'thermal_runaway',
            'battery_chemistry',
            'pv_type',
            'product_type',
            'incident_type_value1',
            'incident_neris_id',
        ]

        if any(col in df.columns for col in neris_indicators):
            return 'NERIS'

        return 'NFIRS'

    def filter_solar_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for solar panel fire incidents (supports both NFIRS and NERIS formats).

        Args:
            df: DataFrame containing NFIRS or NERIS incident data

        Returns:
            DataFrame containing only solar-related incidents
        """
        if df.empty:
            return df

        # Detect data format
        if self.data_format is None:
            self.data_format = self._detect_format(df)

        logger.info(f"Filtering for solar panel incidents ({self.data_format} format)...")

        # Initialize filter mask
        solar_mask = pd.Series([False] * len(df), index=df.index)

        # NERIS-specific filtering (preferred if available)
        if self.data_format == 'NERIS':
            # Filter by NERIS PV type field
            if 'pv_type' in df.columns:
                pv_mask = df['pv_type'].isin(self.neris_pv_types)
                solar_mask |= pv_mask
                logger.info(f"  NERIS PV types matched: {pv_mask.sum()} incidents")

            # Filter by PV ignition source (SOURCE = fire started in PV system)
            if 'pv_ignition_type' in df.columns:
                ignition_mask = df['pv_ignition_type'] == 'SOURCE'
                solar_mask |= ignition_mask
                logger.info(f"  NERIS PV ignition SOURCE: {ignition_mask.sum()} incidents")

        # NFIRS filtering (legacy or fallback)
        # Filter by equipment codes
        if 'item_first_ig' in df.columns:
            equipment_mask = df['item_first_ig'].isin(self.solar_equipment_codes)
            solar_mask |= equipment_mask
            logger.info(f"  Equipment codes matched: {equipment_mask.sum()} incidents")

        # Filter by heat source
        if 'heat_source' in df.columns:
            heat_mask = df['heat_source'].isin(self.solar_heat_sources)
            solar_mask |= heat_mask
            logger.info(f"  Heat source matched: {heat_mask.sum()} incidents")

        # Filter by narrative text (works for both formats)
        if self.use_narrative:
            narrative_cols = [col for col in df.columns if 'narrative' in col.lower() or 'remarks' in col.lower()]

            if narrative_cols:
                narrative_mask = self._check_narrative_keywords(
                    df, narrative_cols, self.solar_keywords
                )
                solar_mask |= narrative_mask
                logger.info(f"  Narrative keywords matched: {narrative_mask.sum()} incidents")

        result = df[solar_mask].copy()
        result['incident_category'] = 'solar_panel'

        logger.info(f"Total solar panel incidents found: {len(result)}")

        return result

    def filter_battery_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for lithium-ion battery fire incidents (supports both NFIRS and NERIS formats).

        Args:
            df: DataFrame containing NFIRS or NERIS incident data

        Returns:
            DataFrame containing only battery-related incidents
        """
        if df.empty:
            return df

        # Detect data format
        if self.data_format is None:
            self.data_format = self._detect_format(df)

        logger.info(f"Filtering for lithium-ion battery incidents ({self.data_format} format)...")

        # Initialize filter mask
        battery_mask = pd.Series([False] * len(df), index=df.index)

        # NERIS-specific filtering (preferred if available)
        if self.data_format == 'NERIS':
            # Filter by thermal runaway (critical NERIS field!)
            if 'thermal_runaway' in df.columns:
                thermal_mask = df['thermal_runaway'] == True
                battery_mask |= thermal_mask
                logger.info(f"  NERIS thermal runaway: {thermal_mask.sum()} incidents")

            # Filter by NERIS product type (hierarchical categories)
            if 'product_type' in df.columns:
                product_mask = df['product_type'].notna()
                # Check if product_type contains battery categories
                for battery_cat in self.neris_battery_products:
                    cat_mask = df['product_type'].astype(str).str.contains(battery_cat, case=False, na=False)
                    battery_mask |= cat_mask
                logger.info(f"  NERIS battery product types matched: {battery_mask.sum()} incidents")

            # Filter by battery chemistry (indicates battery incident)
            if 'battery_chemistry' in df.columns:
                chemistry_mask = df['battery_chemistry'].notna()
                battery_mask |= chemistry_mask
                logger.info(f"  NERIS battery chemistry field: {chemistry_mask.sum()} incidents")

            # Filter by vehicle_battery flag (EV batteries)
            if 'vehicle_battery' in df.columns:
                ev_battery_mask = df['vehicle_battery'] == True
                battery_mask |= ev_battery_mask
                logger.info(f"  NERIS vehicle battery flag: {ev_battery_mask.sum()} incidents")

        # NFIRS filtering (legacy or fallback)
        # Filter by equipment codes
        if 'item_first_ig' in df.columns:
            equipment_mask = df['item_first_ig'].isin(self.battery_equipment_codes)
            battery_mask |= equipment_mask
            logger.info(f"  Battery equipment codes matched: {equipment_mask.sum()} incidents")

        # Filter by heat source
        if 'heat_source' in df.columns:
            heat_mask = df['heat_source'].isin(self.battery_heat_sources)
            battery_mask |= heat_mask
            logger.info(f"  Heat source matched: {heat_mask.sum()} incidents")

        # Filter by incident type (vehicle fires - works for both formats)
        if 'incident_type' in df.columns:
            vehicle_fire_codes = set(range(130, 139))  # Vehicle fire codes
            vehicle_mask = df['incident_type'].isin(vehicle_fire_codes)
            battery_mask |= vehicle_mask
            logger.info(f"  Vehicle fire types matched: {vehicle_mask.sum()} incidents")
        elif 'inc_type' in df.columns:
            vehicle_fire_codes = set(range(130, 139))
            vehicle_mask = df['inc_type'].isin(vehicle_fire_codes)
            battery_mask |= vehicle_mask
            logger.info(f"  Vehicle fire types matched: {vehicle_mask.sum()} incidents")

        # Filter by NERIS hierarchical incident types
        if 'incident_type_value2' in df.columns:
            transport_mask = df['incident_type_value2'] == 'TRANSPORTATION_FIRE'
            battery_mask |= transport_mask
            logger.info(f"  NERIS transportation fires: {transport_mask.sum()} incidents")

        # Filter by mobile property type (EVs - NFIRS)
        if 'prop_type' in df.columns:
            ev_mask = df['prop_type'].isin(self.ev_codes)
            battery_mask |= ev_mask
            logger.info(f"  EV property types matched: {ev_mask.sum()} incidents")

        # Filter by narrative text (works for both formats)
        if self.use_narrative:
            narrative_cols = [col for col in df.columns if 'narrative' in col.lower() or 'remarks' in col.lower()]

            if narrative_cols:
                narrative_mask = self._check_narrative_keywords(
                    df, narrative_cols, self.battery_keywords
                )
                battery_mask |= narrative_mask
                logger.info(f"  Narrative keywords matched: {narrative_mask.sum()} incidents")

        result = df[battery_mask].copy()
        result['incident_category'] = 'lithium_battery'

        logger.info(f"Total lithium-ion battery incidents found: {len(result)}")

        return result

    def filter_all_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for both solar panel and lithium-ion battery incidents.

        Args:
            df: DataFrame containing NFIRS incident data

        Returns:
            DataFrame containing both solar and battery incidents
        """
        logger.info("Filtering for all incident types...")

        solar_incidents = self.filter_solar_incidents(df)
        battery_incidents = self.filter_battery_incidents(df)

        # Combine and remove duplicates
        all_incidents = pd.concat([solar_incidents, battery_incidents], ignore_index=True)
        all_incidents = all_incidents.drop_duplicates()

        logger.info(f"Total combined incidents: {len(all_incidents)}")
        logger.info(f"  Solar: {len(solar_incidents)}")
        logger.info(f"  Battery: {len(battery_incidents)}")

        return all_incidents

    def _check_narrative_keywords(self, df: pd.DataFrame,
                                   narrative_cols: List[str],
                                   keywords: List[str]) -> pd.Series:
        """
        Check narrative text for keyword matches.

        Args:
            df: DataFrame to search
            narrative_cols: List of column names containing narrative text
            keywords: List of keywords to search for

        Returns:
            Boolean Series indicating matches
        """
        mask = pd.Series([False] * len(df), index=df.index)

        for col in narrative_cols:
            if col not in df.columns:
                continue

            # Combine all narrative text for each row
            narratives = df[col].fillna('').astype(str).str.lower()

            # Check for keyword matches
            for keyword in keywords:
                keyword_lower = keyword.lower()
                col_mask = narratives.str.contains(keyword_lower, case=False, na=False, regex=False)
                mask |= col_mask

        return mask

    def add_subcategories(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add subcategories to categorize incidents more specifically.
        Uses NERIS product_type for granular categorization when available.

        Args:
            df: DataFrame with filtered incidents

        Returns:
            DataFrame with subcategory column added
        """
        if df.empty:
            return df

        df = df.copy()
        df['subcategory'] = 'unknown'

        # Detect data format
        if self.data_format is None:
            self.data_format = self._detect_format(df)

        # NERIS-specific granular categorization (preferred)
        if self.data_format == 'NERIS' and 'product_type' in df.columns:
            product_types = df['product_type'].fillna('').astype(str)

            # E-Mobility subcategories
            df.loc[product_types.str.contains('POWER_ASSISTED_BICYCLE', case=False, na=False), 'subcategory'] = 'e_bike'
            df.loc[product_types.str.contains('ELECTRIC_SCOOTER_MOPED', case=False, na=False), 'subcategory'] = 'e_scooter'
            df.loc[product_types.str.contains('PERSONAL_MOBILITY_ASSIST', case=False, na=False), 'subcategory'] = 'mobility_device'

            # Electric Vehicle subcategories
            df.loc[product_types.str.contains('ELECTRIC_VEHICLE', case=False, na=False), 'subcategory'] = 'electric_vehicle'
            df.loc[product_types.str.contains('FULL_ELECTRIC', case=False, na=False), 'subcategory'] = 'ev_full_electric'
            df.loc[product_types.str.contains('PLUG_IN_HYBRID', case=False, na=False), 'subcategory'] = 'ev_plug_in_hybrid'
            df.loc[product_types.str.contains('HYBRID', case=False, na=False), 'subcategory'] = 'ev_hybrid'

            # Energy Storage Systems
            df.loc[product_types.str.contains('ENERGY_STORAGE_SYSTEM', case=False, na=False), 'subcategory'] = 'energy_storage_system'

            # Consumer Products
            df.loc[product_types.str.contains('CELL_PHONE', case=False, na=False), 'subcategory'] = 'cell_phone'
            df.loc[product_types.str.contains('COMPUTER_TABLET', case=False, na=False), 'subcategory'] = 'computer_tablet'
            df.loc[product_types.str.contains('POWER_BANK', case=False, na=False), 'subcategory'] = 'power_bank'
            df.loc[product_types.str.contains('ELECTRONIC_CIGARETTE', case=False, na=False), 'subcategory'] = 'e_cigarette'

            logger.info(f"Applied NERIS product_type categorization")

        # Categorize based on incident type (works for both NFIRS and NERIS)
        incident_type_col = None
        if 'incident_type' in df.columns:
            incident_type_col = 'incident_type'
        elif 'inc_type' in df.columns:
            incident_type_col = 'inc_type'

        if incident_type_col:
            # Building fires
            building_codes = set(range(111, 119))
            building_mask = df[incident_type_col].isin(building_codes) & (df['subcategory'] == 'unknown')
            df.loc[building_mask, 'subcategory'] = 'building_fire'

            # Vehicle fires
            vehicle_codes = set(range(130, 139))
            vehicle_mask = df[incident_type_col].isin(vehicle_codes) & (df['subcategory'] == 'unknown')
            df.loc[vehicle_mask, 'subcategory'] = 'vehicle_fire'

            # Vegetation fires (solar farms)
            vegetation_codes = set(range(140, 144))
            vegetation_mask = df[incident_type_col].isin(vegetation_codes) & (df['subcategory'] == 'unknown')
            df.loc[vegetation_mask, 'subcategory'] = 'vegetation_fire'

            # Outside fires
            outside_codes = set(range(150, 163))
            outside_mask = df[incident_type_col].isin(outside_codes) & (df['subcategory'] == 'unknown')
            df.loc[outside_mask, 'subcategory'] = 'outside_fire'

        # NERIS hierarchical incident type categorization
        if 'incident_type_value2' in df.columns:
            unknown_mask = df['subcategory'] == 'unknown'
            df.loc[unknown_mask & (df['incident_type_value2'] == 'STRUCTURE_FIRE'), 'subcategory'] = 'building_fire'
            df.loc[unknown_mask & (df['incident_type_value2'] == 'TRANSPORTATION_FIRE'), 'subcategory'] = 'vehicle_fire'
            df.loc[unknown_mask & (df['incident_type_value2'] == 'OUTSIDE_FIRE'), 'subcategory'] = 'outside_fire'

        # Further categorize battery incidents (NFIRS fallback)
        if 'incident_category' in df.columns:
            battery_rows = (df['incident_category'] == 'lithium_battery') & (df['subcategory'] == 'unknown')

            # Check for EV-specific indicators (NFIRS)
            if 'prop_type' in df.columns:
                ev_rows = battery_rows & df['prop_type'].isin(self.ev_codes)
                df.loc[ev_rows, 'subcategory'] = 'electric_vehicle'

            # Check for energy storage systems via narrative (NFIRS fallback)
            narrative_cols = [col for col in df.columns if 'narrative' in col.lower()]
            if narrative_cols and self.data_format == 'NFIRS':
                ess_keywords = ['energy storage', 'ESS', 'BESS', 'battery storage']
                ebike_keywords = ['e-bike', 'e bike', 'electric bike', 'electric bicycle']
                escooter_keywords = ['e-scooter', 'e scooter', 'electric scooter']

                for col in narrative_cols:
                    narratives = df[col].fillna('').astype(str).str.lower()

                    # ESS
                    for keyword in ess_keywords:
                        ess_rows = battery_rows & narratives.str.contains(keyword.lower(), case=False, na=False)
                        df.loc[ess_rows, 'subcategory'] = 'energy_storage_system'

                    # E-bikes (NFIRS narrative-based)
                    for keyword in ebike_keywords:
                        ebike_rows = battery_rows & narratives.str.contains(keyword.lower(), case=False, na=False)
                        df.loc[ebike_rows, 'subcategory'] = 'e_bike'

                    # E-scooters (NFIRS narrative-based)
                    for keyword in escooter_keywords:
                        escooter_rows = battery_rows & narratives.str.contains(keyword.lower(), case=False, na=False)
                        df.loc[escooter_rows, 'subcategory'] = 'e_scooter'

        # Add additional NERIS-specific flags
        if self.data_format == 'NERIS':
            # Add thermal runaway flag
            if 'thermal_runaway' in df.columns:
                df['has_thermal_runaway'] = df['thermal_runaway'] == True

            # Add charging status flag
            if 'charging_at_ignition' in df.columns:
                df['was_charging'] = df['charging_at_ignition'] == True

            # Add PV ignition source flag
            if 'pv_ignition_type' in df.columns:
                df['pv_was_source'] = df['pv_ignition_type'] == 'SOURCE'

        return df

    def filter_thermal_runaway_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for incidents with thermal runaway (NERIS-only feature).

        Args:
            df: DataFrame containing NERIS incident data

        Returns:
            DataFrame containing only thermal runaway incidents
        """
        if df.empty:
            return df

        if 'thermal_runaway' not in df.columns:
            logger.warning("thermal_runaway field not found - this is a NERIS-only feature")
            return pd.DataFrame()

        logger.info("Filtering for thermal runaway incidents...")
        result = df[df['thermal_runaway'] == True].copy()
        logger.info(f"Found {len(result)} thermal runaway incidents")

        return result

    def filter_charging_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for incidents where battery was charging at ignition (NERIS-only feature).

        Args:
            df: DataFrame containing NERIS incident data

        Returns:
            DataFrame containing only charging-related incidents
        """
        if df.empty:
            return df

        if 'charging_at_ignition' not in df.columns:
            logger.warning("charging_at_ignition field not found - this is a NERIS-only feature")
            return pd.DataFrame()

        logger.info("Filtering for charging-related incidents...")
        result = df[df['charging_at_ignition'] == True].copy()
        logger.info(f"Found {len(result)} incidents where battery was charging")

        return result

    def get_filter_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics about filtered incidents (supports both NFIRS and NERIS).

        Args:
            df: Filtered DataFrame

        Returns:
            Dictionary containing statistics
        """
        stats = {
            'total_incidents': len(df),
            'data_format': self.data_format,
            'by_category': {},
            'by_subcategory': {},
            'by_year': {},
            'by_state': {},
            'neris_features': {}  # NERIS-specific statistics
        }

        if df.empty:
            return stats

        # Category breakdown
        if 'incident_category' in df.columns:
            stats['by_category'] = df['incident_category'].value_counts().to_dict()

        # Subcategory breakdown
        if 'subcategory' in df.columns:
            stats['by_subcategory'] = df['subcategory'].value_counts().to_dict()

        # Year breakdown
        if 'inc_year' in df.columns:
            stats['by_year'] = df['inc_year'].value_counts().sort_index().to_dict()

        # State breakdown
        if 'state' in df.columns:
            stats['by_state'] = df['state'].value_counts().to_dict()

        # NERIS-specific statistics
        if self.data_format == 'NERIS':
            # Thermal runaway statistics
            if 'thermal_runaway' in df.columns:
                thermal_count = (df['thermal_runaway'] == True).sum()
                stats['neris_features']['thermal_runaway_count'] = int(thermal_count)
                stats['neris_features']['thermal_runaway_pct'] = round(thermal_count / len(df) * 100, 1) if len(df) > 0 else 0

            # Charging statistics
            if 'charging_at_ignition' in df.columns:
                charging_count = (df['charging_at_ignition'] == True).sum()
                stats['neris_features']['charging_related_count'] = int(charging_count)
                stats['neris_features']['charging_related_pct'] = round(charging_count / len(df) * 100, 1) if len(df) > 0 else 0

            # Battery chemistry breakdown
            if 'battery_chemistry' in df.columns:
                stats['neris_features']['by_battery_chemistry'] = df['battery_chemistry'].value_counts().to_dict()

            # Product type breakdown
            if 'product_type' in df.columns:
                stats['neris_features']['by_product_type'] = df['product_type'].value_counts().head(10).to_dict()

            # Safety listed statistics
            if 'safety_listed' in df.columns:
                safety_count = (df['safety_listed'] == True).sum()
                unsafe_count = (df['safety_listed'] == False).sum()
                stats['neris_features']['safety_listed_count'] = int(safety_count)
                stats['neris_features']['not_safety_listed_count'] = int(unsafe_count)

            # PV statistics
            if 'pv_type' in df.columns:
                pv_count = df['pv_type'].notna().sum()
                stats['neris_features']['pv_incidents_count'] = int(pv_count)
                stats['neris_features']['by_pv_type'] = df['pv_type'].value_counts().to_dict()

            if 'pv_ignition_type' in df.columns:
                source_count = (df['pv_ignition_type'] == 'SOURCE').sum()
                target_count = (df['pv_ignition_type'] == 'TARGET').sum()
                stats['neris_features']['pv_was_ignition_source'] = int(source_count)
                stats['neris_features']['pv_was_target'] = int(target_count)

        return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    from data_loader import NFIRSDataLoader, create_sample_data

    # Create sample data
    create_sample_data()

    # Load data
    loader = NFIRSDataLoader()
    modules = loader.load_all_modules()
    merged_data = loader.merge_modules(modules)

    # Filter incidents
    filter_obj = NFIRSIncidentFilter()

    solar = filter_obj.filter_solar_incidents(merged_data)
    battery = filter_obj.filter_battery_incidents(merged_data)
    all_incidents = filter_obj.filter_all_incidents(merged_data)

    # Add subcategories
    all_incidents = filter_obj.add_subcategories(all_incidents)

    # Get statistics
    stats = filter_obj.get_filter_statistics(all_incidents)

    print("\n=== Filter Statistics ===")
    print(f"Total incidents: {stats['total_incidents']}")
    print(f"By category: {stats['by_category']}")
    print(f"By subcategory: {stats['by_subcategory']}")
