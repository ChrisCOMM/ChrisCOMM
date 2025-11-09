"""
NFIRS Data Loader Module

Handles loading and preprocessing NFIRS data from various sources.
"""

import pandas as pd
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class NFIRSDataLoader:
    """Loads and manages NFIRS data from multiple modules."""

    def __init__(self, config_path: str = "config/workflow_config.yml"):
        """
        Initialize the data loader.

        Args:
            config_path: Path to workflow configuration file
        """
        self.config = self._load_config(config_path)
        self.data_sources = self.config.get('data_sources', {})
        self.chunk_size = self.config.get('data_processing', {}).get('chunk_size', 10000)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return {}

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
            # Try reading with ^ delimiter first (NERIS/NFIRS format)
            try:
                df = pd.read_csv(file_path, sep='^', low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} basic incident records (^ delimiter)")
            except:
                # Fall back to comma delimiter
                df = pd.read_csv(file_path, low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} basic incident records (comma delimiter)")

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
            # Try reading with ^ delimiter first (NERIS/NFIRS format)
            try:
                df = pd.read_csv(file_path, sep='^', low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} fire incident records (^ delimiter)")
            except:
                # Fall back to comma delimiter
                df = pd.read_csv(file_path, low_memory=False, encoding='latin-1')
                logger.info(f"Loaded {len(df)} fire incident records (comma delimiter)")

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
        Load all available NFIRS modules.

        Returns:
            Dictionary of DataFrames keyed by module name
        """
        modules = {}

        logger.info("Loading all NFIRS modules...")

        modules['basic'] = self.load_basic_module()
        modules['fire'] = self.load_fire_module()
        modules['structure'] = self.load_structure_module()

        return modules

    def _preprocess_basic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess basic module data.

        Args:
            df: Raw basic module DataFrame

        Returns:
            Preprocessed DataFrame
        """
        # Standardize column names (lowercase and strip quotes)
        df.columns = df.columns.str.lower().str.strip().str.replace('"', '')

        # Convert date fields
        date_fields = ['inc_date', 'alarm', 'arrival', 'inc_cont', 'lu_clear']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Extract year if not present
        if 'inc_date' in df.columns and 'inc_year' not in df.columns:
            df['inc_year'] = df['inc_date'].dt.year

        return df

    def _preprocess_fire(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess fire module data.

        Args:
            df: Raw fire module DataFrame

        Returns:
            Preprocessed DataFrame
        """
        # Standardize column names (lowercase and strip quotes)
        df.columns = df.columns.str.lower().str.strip().str.replace('"', '')

        # Map NERIS/NFIRS column names to expected names
        column_mapping = {
            'heat_sourc': 'heat_source',  # NERIS uses HEAT_SOURC
            'first_ign': 'item_first_ig',  # NERIS uses FIRST_IGN
            'area_orig': 'area_origin',     # NERIS uses AREA_ORIG
        }

        df = df.rename(columns=column_mapping)

        # Convert date fields to match basic module
        date_fields = ['inc_date', 'alarm', 'arrival', 'inc_cont', 'lu_clear']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Convert numeric fields
        numeric_fields = ['num_unit', 'detector_type', 'detector_power',
                          'detector_operation', 'detector_effect', 'detector_fail_reason']

        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')

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


def create_sample_data(output_dir: str = "data") -> None:
    """
    Create sample NFIRS data for testing.

    Args:
        output_dir: Directory to save sample files
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Sample basic module data
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

    # Sample fire module data
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

    logger.info(f"Sample data created in {output_dir}/")


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
