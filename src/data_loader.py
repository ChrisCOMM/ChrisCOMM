"""
NFIRS/NERIS Data Loader Module

Handles loading and preprocessing NFIRS (legacy) and NERIS (current) data from various sources.
Supports both file-based and API-based data access.

NFIRS = National Fire Incident Reporting System (sunsets Feb 2026)
NERIS = National Emergency Response Information System (current)
"""

import pandas as pd
import yaml
import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


# NERIS to NFIRS Column Mapping
# Maps NERIS field names to the expected NFIRS-compatible names used in this project
NERIS_TO_NFIRS_COLUMNS = {
    # Fire Module Fields
    'heat_sourc': 'heat_source',
    'first_ign': 'item_first_ig',
    'area_orig': 'area_origin',
    'cause_ign': 'cause_ignition',
    'fact_ign_1': 'factor_contrib_ign_1',
    'fact_ign_2': 'factor_contrib_ign_2',
    'hum_fact_1': 'human_factor_1',
    'hum_fact_2': 'human_factor_2',
    'det_type': 'detector_type',
    'det_power': 'detector_power',
    'det_operat': 'detector_operation',
    'det_effect': 'detector_effect',
    'det_fail': 'detector_fail_reason',
    'struc_type': 'structure_type',
    'struc_stat': 'structure_status',

    # Incident Fields
    'inc_type': 'incident_type',
    'inc_no': 'incident_number',
    'inc_cont': 'incident_contained',

    # Property Fields
    'prop_use': 'property_use',
    'prop_loss': 'property_loss',
    'cont_loss': 'contents_loss',

    # Casualty Fields
    'ff_death': 'ff_deaths',
    'oth_death': 'civilian_deaths',
    'ff_inj': 'ff_injuries',
    'oth_inj': 'civilian_injuries',
}

# NERIS-specific field mappings for enhanced features
NERIS_BATTERY_FIELDS = [
    'thermal_runaway',
    'charging_at_ignition',
    'battery_chemistry',
    'battery_cell',
    'battery_size_voltage',
    'battery_size_amp_hour',
    'battery_size_watt_hour',
    'battery_charge',
    'safety_listed',
    'original_battery',
    'vehicle_battery',
    'product_type',
    'installation_status',
    'incident_indoor_outdoor',
    'in_direct_sunlight',
    'impacted_from_source',
    'fd_suppression',
]

NERIS_PV_FIELDS = [
    'pv_type',
    'pv_ignition_type',
    'pv_panel_type',
]


class NFIRSDataLoader:
    """
    Loads and manages NFIRS (legacy) and NERIS (current) data from multiple sources.

    Supports:
    - NFIRS format (comma delimiter, numeric codes)
    - NERIS format (caret delimiter, hierarchical codes)
    - Automatic format detection
    - File-based and API-based data loading
    - Battery and solar PV specific fields
    """

    def __init__(self, config_path: str = "config/workflow_config.yml"):
        """
        Initialize the data loader.

        Args:
            config_path: Path to workflow configuration file
        """
        self.config = self._load_config(config_path)
        self.data_sources = self.config.get('data_sources', {})
        self.chunk_size = self.config.get('data_processing', {}).get('chunk_size', 10000)
        self.data_format = None  # Will be auto-detected: 'NFIRS' or 'NERIS'

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
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
            'incident_neris_id',
            'incident_final_type',
            'thermal_runaway',
            'battery_chemistry',
            'pv_type',
        ]

        if any(col in df.columns for col in neris_indicators):
            logger.info("Detected NERIS data format")
            return 'NERIS'

        # Check for hierarchical incident types (NERIS uses arrays/nested structures)
        if 'incident_type' in df.columns:
            sample = df['incident_type'].dropna().head(1)
            if len(sample) > 0 and isinstance(sample.iloc[0], (list, dict, str)):
                if isinstance(sample.iloc[0], str) and ':' in sample.iloc[0]:
                    logger.info("Detected NERIS data format (hierarchical types)")
                    return 'NERIS'

        logger.info("Detected NFIRS data format")
        return 'NFIRS'

    def _parse_neris_incident_type(self, incident_type: Any) -> Dict[str, str]:
        """
        Parse NERIS hierarchical incident type into components.

        NERIS uses hierarchical types like:
        "FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE"

        Args:
            incident_type: NERIS incident type (string, list, or dict)

        Returns:
            Dict with value_1, value_2, value_3, and nfirs_equivalent
        """
        result = {
            'value_1': None,
            'value_2': None,
            'value_3': None,
            'nfirs_equivalent': None,
        }

        if pd.isna(incident_type):
            return result

        # Handle string format: "FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE"
        if isinstance(incident_type, str):
            parts = [p.strip() for p in incident_type.split(':')]
            result['value_1'] = parts[0] if len(parts) > 0 else None
            result['value_2'] = parts[1] if len(parts) > 1 else None
            result['value_3'] = parts[2] if len(parts) > 2 else None

        # Handle list format: ['FIRE', 'STRUCTURE_FIRE', 'ROOM_AND_CONTENTS_FIRE']
        elif isinstance(incident_type, list):
            result['value_1'] = incident_type[0] if len(incident_type) > 0 else None
            result['value_2'] = incident_type[1] if len(incident_type) > 1 else None
            result['value_3'] = incident_type[2] if len(incident_type) > 2 else None

        # Handle dict format: {'value_1': 'FIRE', 'value_2': 'STRUCTURE_FIRE', ...}
        elif isinstance(incident_type, dict):
            result['value_1'] = incident_type.get('value_1')
            result['value_2'] = incident_type.get('value_2')
            result['value_3'] = incident_type.get('value_3')

        # Map to NFIRS equivalent (simplified mapping)
        if result['value_1'] == 'FIRE':
            if result['value_2'] == 'STRUCTURE_FIRE':
                result['nfirs_equivalent'] = '111'  # Building fire
            elif result['value_2'] == 'TRANSPORTATION_FIRE':
                result['nfirs_equivalent'] = '131'  # Vehicle fire
            elif result['value_2'] == 'OUTSIDE_FIRE':
                result['nfirs_equivalent'] = '141'  # Vegetation fire

        return result

    def _extract_battery_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract NERIS battery incident module fields if present.

        Args:
            df: DataFrame to process

        Returns:
            DataFrame with battery fields extracted/renamed
        """
        # Check if any battery fields exist
        battery_cols = [col for col in NERIS_BATTERY_FIELDS if col in df.columns]

        if battery_cols:
            logger.info(f"Found {len(battery_cols)} NERIS battery fields: {battery_cols}")
            # Ensure boolean fields are properly typed
            bool_fields = ['thermal_runaway', 'charging_at_ignition', 'safety_listed',
                          'original_battery', 'vehicle_battery', 'installation_status',
                          'in_direct_sunlight', 'impacted_from_source']
            for field in bool_fields:
                if field in df.columns:
                    df[field] = df[field].map({'True': True, 'true': True, True: True,
                                               'False': False, 'false': False, False: False})

        return df

    def _extract_pv_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract NERIS solar PV fields if present.

        Args:
            df: DataFrame to process

        Returns:
            DataFrame with PV fields extracted/renamed
        """
        pv_cols = [col for col in NERIS_PV_FIELDS if col in df.columns]

        if pv_cols:
            logger.info(f"Found {len(pv_cols)} NERIS PV fields: {pv_cols}")

        return df

    def load_basic_module(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load NFIRS Basic Module data.

        Args:
            file_path: Path to basic module CSV file

        Returns:
            DataFrame containing basic incident data
        """
        if file_path is None:
            file_path = self.data_sources.get('nfirs_basic_module')

        if not file_path or not Path(file_path).exists():
            logger.warning(f"Basic module file not found: {file_path}")
            return pd.DataFrame()

        logger.info(f"Loading basic module from {file_path}")

        try:
            # Try reading with ^ delimiter first (NERIS format)
            df = pd.read_csv(file_path, sep='^', low_memory=False, encoding='latin-1')
            # Check if delimiter worked (more than 1 column means it worked)
            if len(df.columns) > 1:
                logger.info(f"Loaded {len(df)} basic incident records (^ delimiter - NERIS format)")
            else:
                # Fall back to comma delimiter (NFIRS format)
                df = pd.read_csv(file_path, sep=',', low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} basic incident records (comma delimiter - NFIRS format)")

            return self._preprocess_basic(df)
        except Exception as e:
            logger.error(f"Error loading basic module: {e}")
            return pd.DataFrame()

    def load_fire_module(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load NFIRS Fire Module data.

        Args:
            file_path: Path to fire module CSV file

        Returns:
            DataFrame containing fire incident data
        """
        if file_path is None:
            file_path = self.data_sources.get('nfirs_fire_module')

        if not file_path or not Path(file_path).exists():
            logger.warning(f"Fire module file not found: {file_path}")
            return pd.DataFrame()

        logger.info(f"Loading fire module from {file_path}")

        try:
            # Try reading with ^ delimiter first (NERIS format)
            df = pd.read_csv(file_path, sep='^', low_memory=False, encoding='latin-1')
            # Check if delimiter worked (more than 1 column means it worked)
            if len(df.columns) > 1:
                logger.info(f"Loaded {len(df)} fire incident records (^ delimiter - NERIS format)")
            else:
                # Fall back to comma delimiter (NFIRS format)
                df = pd.read_csv(file_path, sep=',', low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} fire incident records (comma delimiter - NFIRS format)")

            return self._preprocess_fire(df)
        except Exception as e:
            logger.error(f"Error loading fire module: {e}")
            return pd.DataFrame()

    def load_structure_module(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load NFIRS Structure Fire Module data.

        Args:
            file_path: Path to structure fire module CSV file

        Returns:
            DataFrame containing structure fire data
        """
        if file_path is None:
            file_path = self.data_sources.get('nfirs_structure_module')

        if not file_path or not Path(file_path).exists():
            logger.warning(f"Structure module file not found: {file_path}")
            return pd.DataFrame()

        logger.info(f"Loading structure module from {file_path}")

        try:
            df = pd.read_csv(file_path, low_memory=False, encoding='latin-1')
            logger.info(f"Loaded {len(df)} structure fire records")
            return df
        except Exception as e:
            logger.error(f"Error loading structure module: {e}")
            return pd.DataFrame()

    def load_all_modules(self) -> Dict[str, pd.DataFrame]:
        """
        Load all available NFIRS/NERIS modules.

        Returns:
            Dictionary of DataFrames keyed by module name
        """
        modules = {}

        logger.info("Loading all data modules...")

        # Check if NERIS API should be used
        use_neris_api = self.data_sources.get('use_neris_api', False)

        if use_neris_api:
            logger.info("Loading data from NERIS API")
            try:
                modules = self.load_from_neris_api()
            except Exception as e:
                logger.error(f"Failed to load from NERIS API: {e}")
                logger.info("Falling back to file-based loading")
                modules['basic'] = self.load_basic_module()
                modules['fire'] = self.load_fire_module()
                modules['structure'] = self.load_structure_module()
        else:
            modules['basic'] = self.load_basic_module()
            modules['fire'] = self.load_fire_module()
            modules['structure'] = self.load_structure_module()

        return modules

    def load_from_neris_api(self, **query_params) -> Dict[str, pd.DataFrame]:
        """
        Load incident data from NERIS API.

        Args:
            **query_params: API query parameters (start_date, end_date, incident_type, etc.)

        Returns:
            Dictionary of DataFrames keyed by module name

        Example:
            loader.load_from_neris_api(
                start_date='2024-01-01',
                end_date='2024-12-31',
                incident_type='FIRE'
            )
        """
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed. Install with: pip install requests")
            return {}

        api_endpoint = self.data_sources.get('neris_api_endpoint', 'https://api.neris.fsri.org/v1')
        api_key = self.data_sources.get('neris_api_key') or os.environ.get('NERIS_API_KEY')

        if not api_key:
            logger.error("NERIS API key not found. Set NERIS_API_KEY environment variable or configure in settings.")
            return {}

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Merge default params with provided params
        default_params = {
            'start_date': query_params.get('start_date', '2024-01-01'),
            'end_date': query_params.get('end_date', '2024-12-31'),
            'limit': query_params.get('limit', 10000),
        }

        params = {**default_params, **query_params}

        logger.info(f"Fetching data from NERIS API: {api_endpoint}/incidents")
        logger.info(f"  Parameters: {params}")

        try:
            response = requests.get(
                f"{api_endpoint}/incidents",
                headers=headers,
                params=params,
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            # Convert API response to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'incidents' in data:
                df = pd.DataFrame(data['incidents'])
            else:
                logger.error(f"Unexpected API response format: {type(data)}")
                return {}

            logger.info(f"Loaded {len(df)} incidents from NERIS API")

            # Process the data through preprocessing
            df = self._preprocess_basic(df)

            # For NERIS API data, incident and fire data are typically combined
            modules = {
                'basic': df,
                'fire': df,  # NERIS combines these
                'structure': df,
            }

            return modules

        except requests.exceptions.RequestException as e:
            logger.error(f"NERIS API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"  Response: {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"Error processing NERIS API data: {e}")
            return {}

    def _preprocess_basic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess basic/incident module data (supports both NFIRS and NERIS formats).

        Args:
            df: Raw basic module DataFrame

        Returns:
            Preprocessed DataFrame
        """
        # Standardize column names (lowercase and strip quotes)
        df.columns = df.columns.str.lower().str.strip().str.replace('"', '')

        # Detect data format
        if self.data_format is None:
            self.data_format = self._detect_format(df)

        # Apply column mapping
        df = df.rename(columns=NERIS_TO_NFIRS_COLUMNS)

        # Parse NERIS incident types
        if self.data_format == 'NERIS' and 'incident_final_type' in df.columns:
            logger.info("Parsing NERIS hierarchical incident types")
            type_parsed = df['incident_final_type'].apply(self._parse_neris_incident_type)
            df['incident_type_value1'] = type_parsed.apply(lambda x: x['value_1'])
            df['incident_type_value2'] = type_parsed.apply(lambda x: x['value_2'])
            df['incident_type_value3'] = type_parsed.apply(lambda x: x['value_3'])
            # Map to NFIRS-compatible incident_type for backward compatibility
            df['incident_type'] = type_parsed.apply(lambda x: x['nfirs_equivalent'])

        # Convert date fields
        date_fields = ['inc_date', 'alarm', 'arrival', 'incident_contained', 'lu_clear']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Extract year if not present
        if 'inc_date' in df.columns and 'inc_year' not in df.columns:
            df['inc_year'] = df['inc_date'].dt.year

        logger.info(f"Preprocessed {self.data_format} basic/incident data")

        return df

    def _preprocess_fire(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess fire module data (supports both NFIRS and NERIS formats).

        Args:
            df: Raw fire module DataFrame

        Returns:
            Preprocessed DataFrame
        """
        # Standardize column names (lowercase and strip quotes)
        df.columns = df.columns.str.lower().str.strip().str.replace('"', '')

        # Detect data format
        if self.data_format is None:
            self.data_format = self._detect_format(df)

        # Apply NERIS to NFIRS column mapping
        df = df.rename(columns=NERIS_TO_NFIRS_COLUMNS)

        # Extract NERIS-specific battery fields
        df = self._extract_battery_fields(df)

        # Extract NERIS-specific PV fields
        df = self._extract_pv_fields(df)

        # Parse hierarchical incident types if NERIS format
        if self.data_format == 'NERIS' and 'incident_final_type' in df.columns:
            logger.info("Parsing NERIS hierarchical incident types")
            type_parsed = df['incident_final_type'].apply(self._parse_neris_incident_type)
            df['incident_type_value1'] = type_parsed.apply(lambda x: x['value_1'])
            df['incident_type_value2'] = type_parsed.apply(lambda x: x['value_2'])
            df['incident_type_value3'] = type_parsed.apply(lambda x: x['value_3'])
            df['incident_type_nfirs'] = type_parsed.apply(lambda x: x['nfirs_equivalent'])

        # Convert date fields to match basic module
        date_fields = ['inc_date', 'alarm', 'arrival', 'incident_contained', 'lu_clear']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Convert numeric fields
        numeric_fields = ['num_unit', 'detector_type', 'detector_power',
                          'detector_operation', 'detector_effect', 'detector_fail_reason',
                          'battery_size_voltage', 'battery_size_amp_hour',
                          'battery_size_watt_hour', 'battery_charge']

        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')

        # Log format and available fields
        logger.info(f"Preprocessed {self.data_format} fire module data")
        if 'thermal_runaway' in df.columns:
            logger.info(f"  - Found battery incident data")
        if any(col.startswith('pv_') for col in df.columns):
            logger.info(f"  - Found PV/solar data")

        return df

    def merge_modules(self, modules: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Merge multiple NFIRS modules on incident identifiers.

        Args:
            modules: Dictionary of DataFrames to merge

        Returns:
            Merged DataFrame
        """
        if not modules or 'basic' not in modules:
            logger.error("Basic module required for merging")
            return pd.DataFrame()

        result = modules['basic']

        # Define merge keys (common NFIRS identifiers)
        merge_keys = ['state', 'fdid', 'inc_date', 'inc_no', 'exp_no']

        # Merge fire module
        if 'fire' in modules and not modules['fire'].empty:
            # Find available merge keys
            available_keys = [k for k in merge_keys if k in result.columns and k in modules['fire'].columns]

            if available_keys:
                logger.info(f"Merging fire module on {available_keys}")
                result = result.merge(
                    modules['fire'],
                    on=available_keys,
                    how='left',
                    suffixes=('', '_fire')
                )

        # Merge structure module
        if 'structure' in modules and not modules['structure'].empty:
            available_keys = [k for k in merge_keys if k in result.columns and k in modules['structure'].columns]

            if available_keys:
                logger.info(f"Merging structure module on {available_keys}")
                result = result.merge(
                    modules['structure'],
                    on=available_keys,
                    how='left',
                    suffixes=('', '_structure')
                )

        logger.info(f"Merged dataset contains {len(result)} records with {len(result.columns)} columns")

        return result


def create_sample_data(output_dir: str = "data", format: str = "NFIRS") -> None:
    """
    Create sample NFIRS or NERIS data for testing.

    Args:
        output_dir: Directory to save sample files
        format: Data format - 'NFIRS' or 'NERIS'
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    if format.upper() == "NFIRS":
        # Sample NFIRS basic module data
        basic_data = {
            'state': ['CA', 'TX', 'FL', 'NY', 'AZ'],
            'fdid': ['12345', '23456', '34567', '45678', '56789'],
            'inc_date': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12'],
            'inc_no': ['001', '002', '003', '004', '005'],
            'exp_no': ['00', '00', '00', '00', '00'],
            'inc_type': ['111', '131', '111', '142', '111'],
            'aid': ['3', '3', '3', '3', '3'],
            'alarm': ['2024-01-15 10:30', '2024-02-20 14:15', '2024-03-10 09:45', '2024-04-05 16:20', '2024-05-12 11:00'],
            'arrival': ['2024-01-15 10:35', '2024-02-20 14:20', '2024-03-10 09:50', '2024-04-05 16:25', '2024-05-12 11:05'],
            'prop_use': ['429', '961', '429', '961', '419'],
        }

        # Sample NFIRS fire module data
        fire_data = {
            'state': ['CA', 'TX', 'FL', 'NY', 'AZ'],
            'fdid': ['12345', '23456', '34567', '45678', '56789'],
            'inc_date': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12'],
            'inc_no': ['001', '002', '003', '004', '005'],
            'exp_no': ['00', '00', '00', '00', '00'],
            'heat_source': ['87', '82', '61', '62', '87'],
            'item_first_ig': ['262', '919', '261', '131', '262'],
            'cause_ign': ['31', '40', '41', '42', '33'],
            'area_origin': ['41', '85', '51', '86', '41'],
        }

        pd.DataFrame(basic_data).to_csv(f"{output_dir}/basicincident.csv", index=False)
        pd.DataFrame(fire_data).to_csv(f"{output_dir}/fireincident.csv", index=False)

        logger.info(f"Sample NFIRS data created in {output_dir}/")

    else:  # NERIS format
        # Sample NERIS incident data with battery and PV fields
        neris_data = {
            'state': ['CA', 'TX', 'FL', 'NY', 'AZ', 'WA'],
            'fdid': ['12345', '23456', '34567', '45678', '56789', '67890'],
            'incident_neris_id': ['FD12345:1705318200', 'FD23456:1708442100', 'FD34567:1710075000',
                                  'FD45678:1712001600', 'FD56789:1715515200', 'FD67890:1718107200'],
            'incident_internal_id': ['CA-001', 'TX-002', 'FL-003', 'NY-004', 'AZ-005', 'WA-006'],
            'inc_date': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12', '2024-06-11'],
            'incident_final_type': [
                'FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE',
                'FIRE: TRANSPORTATION_FIRE: VEHICLE_FIRE_PASSENGER',
                'FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE',
                'FIRE: OUTSIDE_FIRE: VEGETATION_GRASS_FIRE',
                'FIRE: STRUCTURE_FIRE: ROOM_AND_CONTENTS_FIRE',
                'FIRE: TRANSPORTATION_FIRE: POWERED_MOBILITY_DEVICE_FIRE'
            ],
            'alarm': ['2024-01-15 10:30', '2024-02-20 14:15', '2024-03-10 09:45', '2024-04-05 16:20', '2024-05-12 11:00', '2024-06-11 08:30'],
            'arrival': ['2024-01-15 10:35', '2024-02-20 14:20', '2024-03-10 09:50', '2024-04-05 16:25', '2024-05-12 11:05', '2024-06-11 08:35'],

            # Battery fields
            'thermal_runaway': [False, True, False, False, False, True],
            'charging_at_ignition': [False, True, False, False, False, True],
            'battery_chemistry': [None, 'LITHIUM_ION', None, None, None, 'LITHIUM_ION'],
            'battery_charge': [None, 75, None, None, None, 50],
            'safety_listed': [None, False, None, None, None, True],
            'vehicle_battery': [False, True, False, False, False, False],
            'product_type': [None, 'ELECTRIC_VEHICLE: CAR_RR: FULL_ELECTRIC', None, None, None, 'E_MOBILITY: POWER_ASSISTED_BICYCLE'],

            # PV fields
            'pv_type': ['PANEL_POWER_GENERATION', None, None, None, 'PANEL_POWER_GENERATION', None],
            'pv_ignition_type': ['SOURCE', None, None, None, 'SOURCE', None],
        }

        # Save as caret-delimited (NERIS format)
        pd.DataFrame(neris_data).to_csv(f"{output_dir}/neris_incidents.csv", sep='^', index=False)

        logger.info(f"Sample NERIS data created in {output_dir}/")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create sample data for testing
    create_sample_data()

    # Test data loader
    loader = NFIRSDataLoader()
    modules = loader.load_all_modules()
    merged = loader.merge_modules(modules)

    print(f"\nLoaded {len(merged)} total records")
    print(f"Columns: {list(merged.columns)}")
