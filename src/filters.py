"""
NFIRS Incident Filters Module

Filters NFIRS data for solar panel and lithium-ion battery incidents.
"""

import pandas as pd
import yaml
import logging
import re
from typing import List, Dict, Set, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class NFIRSIncidentFilter:
    """Filters NFIRS incidents for specific equipment types."""

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

    def filter_solar_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for solar panel fire incidents.

        Args:
            df: DataFrame containing NFIRS incident data

        Returns:
            DataFrame containing only solar-related incidents
        """
        if df.empty:
            return df

        logger.info("Filtering for solar panel incidents...")

        # Initialize filter mask
        solar_mask = pd.Series([False] * len(df), index=df.index)

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

        # Filter by narrative text
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
        Filter for lithium-ion battery fire incidents.

        Args:
            df: DataFrame containing NFIRS incident data

        Returns:
            DataFrame containing only battery-related incidents
        """
        if df.empty:
            return df

        logger.info("Filtering for lithium-ion battery incidents...")

        # Initialize filter mask
        battery_mask = pd.Series([False] * len(df), index=df.index)

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

        # Filter by incident type (vehicle fires)
        if 'inc_type' in df.columns:
            vehicle_fire_codes = set(range(130, 139))  # Vehicle fire codes
            vehicle_mask = df['inc_type'].isin(vehicle_fire_codes)
            battery_mask |= vehicle_mask
            logger.info(f"  Vehicle fire types matched: {vehicle_mask.sum()} incidents")

        # Filter by mobile property type (EVs)
        if 'prop_type' in df.columns:
            ev_mask = df['prop_type'].isin(self.ev_codes)
            battery_mask |= ev_mask
            logger.info(f"  EV property types matched: {ev_mask.sum()} incidents")

        # Filter by narrative text
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

        Args:
            df: DataFrame with filtered incidents

        Returns:
            DataFrame with subcategory column added
        """
        if df.empty:
            return df

        df = df.copy()
        df['subcategory'] = 'unknown'

        # Categorize based on incident type
        if 'inc_type' in df.columns:
            # Building fires
            building_codes = set(range(111, 119))
            df.loc[df['inc_type'].isin(building_codes), 'subcategory'] = 'building_fire'

            # Vehicle fires
            vehicle_codes = set(range(130, 139))
            df.loc[df['inc_type'].isin(vehicle_codes), 'subcategory'] = 'vehicle_fire'

            # Vegetation fires (solar farms)
            vegetation_codes = set(range(140, 144))
            df.loc[df['inc_type'].isin(vegetation_codes), 'subcategory'] = 'vegetation_fire'

            # Outside fires
            outside_codes = set(range(150, 163))
            df.loc[df['inc_type'].isin(outside_codes), 'subcategory'] = 'outside_fire'

        # Further categorize battery incidents
        if 'incident_category' in df.columns:
            battery_rows = df['incident_category'] == 'lithium_battery'

            # Check for EV-specific indicators
            if 'prop_type' in df.columns:
                ev_rows = battery_rows & df['prop_type'].isin(self.ev_codes)
                df.loc[ev_rows, 'subcategory'] = 'electric_vehicle'

            # Check for energy storage systems
            narrative_cols = [col for col in df.columns if 'narrative' in col.lower()]
            if narrative_cols:
                ess_keywords = ['energy storage', 'ESS', 'BESS', 'battery storage']
                for col in narrative_cols:
                    narratives = df[col].fillna('').astype(str).str.lower()
                    for keyword in ess_keywords:
                        ess_rows = battery_rows & narratives.str.contains(keyword.lower(), case=False, na=False)
                        df.loc[ess_rows, 'subcategory'] = 'energy_storage_system'

        return df

    def get_filter_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics about filtered incidents.

        Args:
            df: Filtered DataFrame

        Returns:
            Dictionary containing statistics
        """
        stats = {
            'total_incidents': len(df),
            'by_category': {},
            'by_subcategory': {},
            'by_year': {},
            'by_state': {}
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
