"""
NFIRS Data Analysis Module

Performs statistical and trend analysis on filtered NFIRS incidents.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class NFIRSAnalyzer:
    """Analyzes NFIRS incident data for trends and patterns."""

    def __init__(self):
        """Initialize the analyzer."""
        pass

    def temporal_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Analyze temporal trends in incidents.

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing temporal analysis results
        """
        if df.empty or 'inc_date' not in df.columns:
            logger.warning("No date information available for temporal analysis")
            return {}

        logger.info("Performing temporal analysis...")

        results = {}

        # Ensure inc_date is datetime
        df = df.copy()
        df['inc_date'] = pd.to_datetime(df['inc_date'], errors='coerce')

        # Remove rows with invalid dates
        df = df.dropna(subset=['inc_date'])

        if df.empty:
            return {}

        # Extract time components
        df['year'] = df['inc_date'].dt.year
        df['month'] = df['inc_date'].dt.month
        df['quarter'] = df['inc_date'].dt.quarter
        df['day_of_week'] = df['inc_date'].dt.dayofweek
        df['hour'] = df['inc_date'].dt.hour

        # Yearly trends
        results['yearly'] = df.groupby('year').size().to_dict()

        # Monthly trends (across all years)
        results['by_month'] = df.groupby('month').size().to_dict()

        # Quarterly trends (convert tuple keys to strings for JSON compatibility)
        quarterly_dict = df.groupby(['year', 'quarter']).size().to_dict()
        results['quarterly'] = {f"{k[0]}_Q{k[1]}": v for k, v in quarterly_dict.items()}

        # Day of week patterns
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = df.groupby('day_of_week').size()
        results['by_day_of_week'] = {day_names[i]: dow_counts.get(i, 0) for i in range(7)}

        # Time series data for plotting (convert datetime keys to strings)
        time_series_dict = df.groupby('inc_date').size().to_dict()
        results['time_series'] = {k.isoformat() if hasattr(k, 'isoformat') else str(k): v
                                  for k, v in time_series_dict.items()}

        # Growth rate calculation
        yearly_df = df.groupby('year').size().reset_index(name='count')
        if len(yearly_df) > 1:
            yearly_df['growth_rate'] = yearly_df['count'].pct_change() * 100
            results['yearly_growth_rate'] = yearly_df.set_index('year')['growth_rate'].to_dict()

        logger.info(f"Temporal analysis complete: {len(df)} incidents analyzed")

        return results

    def geographic_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Analyze geographic distribution of incidents.

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing geographic analysis results
        """
        if df.empty:
            return {}

        logger.info("Performing geographic analysis...")

        results = {}

        # State-level analysis
        if 'state' in df.columns:
            state_counts = df['state'].value_counts()
            results['by_state'] = state_counts.to_dict()
            results['top_10_states'] = state_counts.head(10).to_dict()

        # County-level analysis (if available) - convert tuple keys to strings
        if 'county' in df.columns:
            county_counts = df.groupby(['state', 'county']).size()
            results['by_county'] = {f"{k[0]}_{k[1]}": v for k, v in county_counts.to_dict().items()}

        # Urban vs rural (based on FDID patterns or population)
        if 'fdid' in df.columns:
            results['unique_departments'] = df['fdid'].nunique()

        # Regional grouping (if state data available)
        if 'state' in df.columns:
            regions = self._assign_regions(df['state'])
            regional_counts = regions.value_counts()
            results['by_region'] = regional_counts.to_dict()

        logger.info(f"Geographic analysis complete: {len(results)} metrics calculated")

        return results

    def casualty_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Analyze casualties (deaths and injuries).

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing casualty analysis results
        """
        if df.empty:
            return {}

        logger.info("Performing casualty analysis...")

        results = {
            'total_incidents': len(df),
            'incidents_with_casualties': 0,
            'total_deaths': 0,
            'total_injuries': 0,
            'firefighter_deaths': 0,
            'firefighter_injuries': 0,
            'civilian_deaths': 0,
            'civilian_injuries': 0
        }

        # Death and injury columns (various naming conventions in NFIRS)
        death_cols = ['death', 'deaths', 'ff_death', 'oth_death', 'civ_death']
        injury_cols = ['inj', 'injuries', 'ff_inj', 'oth_inj', 'civ_inj']

        # Sum deaths
        for col in death_cols:
            if col in df.columns:
                col_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
                results['total_deaths'] += col_sum

                if 'ff' in col:
                    results['firefighter_deaths'] += col_sum
                elif 'civ' in col or 'oth' in col:
                    results['civilian_deaths'] += col_sum

        # Sum injuries
        for col in injury_cols:
            if col in df.columns:
                col_sum = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
                results['total_injuries'] += col_sum

                if 'ff' in col:
                    results['firefighter_injuries'] += col_sum
                elif 'civ' in col or 'oth' in col:
                    results['civilian_injuries'] += col_sum

        # Count incidents with any casualties
        has_casualty = False
        casualty_cols = death_cols + injury_cols
        for col in casualty_cols:
            if col in df.columns:
                casualties = pd.to_numeric(df[col], errors='coerce').fillna(0)
                has_casualty |= (casualties > 0)

        if isinstance(has_casualty, pd.Series):
            results['incidents_with_casualties'] = has_casualty.sum()

        # Calculate rates
        if results['total_incidents'] > 0:
            results['casualty_rate'] = (results['incidents_with_casualties'] /
                                       results['total_incidents'] * 100)
            results['fatality_rate'] = (results['total_deaths'] /
                                       results['total_incidents'] * 100)

        logger.info(f"Casualty analysis complete: {results['total_deaths']} deaths, "
                   f"{results['total_injuries']} injuries")

        return results

    def property_loss_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Analyze property loss and damage.

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing property loss analysis
        """
        if df.empty:
            return {}

        logger.info("Performing property loss analysis...")

        results = {}

        # Property loss columns
        loss_cols = ['prop_loss', 'cont_loss', 'prop_val', 'cont_val']

        for col in loss_cols:
            if col in df.columns:
                losses = pd.to_numeric(df[col], errors='coerce').fillna(0)

                results[f'{col}_total'] = float(losses.sum())
                results[f'{col}_mean'] = float(losses.mean())
                results[f'{col}_median'] = float(losses.median())
                results[f'{col}_max'] = float(losses.max())

        # Total property loss
        if 'prop_loss' in df.columns:
            total_loss = pd.to_numeric(df['prop_loss'], errors='coerce').fillna(0).sum()
            results['total_property_loss'] = float(total_loss)

            # Loss distribution
            losses = pd.to_numeric(df['prop_loss'], errors='coerce').fillna(0)
            results['loss_distribution'] = {
                'under_10k': int((losses < 10000).sum()),
                '10k_to_100k': int(((losses >= 10000) & (losses < 100000)).sum()),
                '100k_to_1m': int(((losses >= 100000) & (losses < 1000000)).sum()),
                'over_1m': int((losses >= 1000000).sum())
            }

        logger.info(f"Property loss analysis complete")

        return results

    def incident_characteristics(self, df: pd.DataFrame) -> Dict:
        """
        Analyze incident characteristics (causes, areas of origin, etc.).

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing incident characteristic analysis
        """
        if df.empty:
            return {}

        logger.info("Analyzing incident characteristics...")

        results = {}

        # Incident types
        if 'inc_type' in df.columns:
            results['incident_types'] = df['inc_type'].value_counts().head(10).to_dict()

        # Areas of origin
        if 'area_origin' in df.columns:
            results['areas_of_origin'] = df['area_origin'].value_counts().head(10).to_dict()

        # Heat sources
        if 'heat_source' in df.columns:
            results['heat_sources'] = df['heat_source'].value_counts().head(10).to_dict()

        # Equipment involved
        if 'item_first_ig' in df.columns:
            results['equipment_involved'] = df['item_first_ig'].value_counts().head(10).to_dict()

        # Causes of ignition
        if 'cause_ign' in df.columns:
            results['ignition_causes'] = df['cause_ign'].value_counts().head(10).to_dict()

        # Fire spread
        if 'fire_sprd' in df.columns:
            results['fire_spread'] = df['fire_sprd'].value_counts().to_dict()

        # Detector presence and operation
        if 'detector_type' in df.columns:
            results['detector_types'] = df['detector_type'].value_counts().to_dict()

        if 'detector_operation' in df.columns:
            results['detector_operation'] = df['detector_operation'].value_counts().to_dict()

        # Categories and subcategories
        if 'incident_category' in df.columns:
            results['by_category'] = df['incident_category'].value_counts().to_dict()

        if 'subcategory' in df.columns:
            results['by_subcategory'] = df['subcategory'].value_counts().to_dict()

        logger.info(f"Incident characteristics analysis complete")

        return results

    def comparative_analysis(self, df: pd.DataFrame,
                           category_col: str = 'incident_category') -> Dict:
        """
        Compare different incident categories.

        Args:
            df: DataFrame containing incident data
            category_col: Column name to use for comparison

        Returns:
            Dictionary containing comparative analysis
        """
        if df.empty or category_col not in df.columns:
            return {}

        logger.info(f"Performing comparative analysis by {category_col}...")

        results = {}
        categories = df[category_col].unique()

        for category in categories:
            cat_df = df[df[category_col] == category]

            results[str(category)] = {
                'count': len(cat_df),
                'percentage': len(cat_df) / len(df) * 100 if len(df) > 0 else 0
            }

            # Temporal trends by category
            if 'inc_year' in cat_df.columns:
                results[str(category)]['yearly_trend'] = (
                    cat_df['inc_year'].value_counts().sort_index().to_dict()
                )

            # Average casualties by category
            if 'death' in cat_df.columns:
                deaths = pd.to_numeric(cat_df['death'], errors='coerce').fillna(0)
                results[str(category)]['avg_deaths'] = float(deaths.mean())

            if 'inj' in cat_df.columns:
                injuries = pd.to_numeric(cat_df['inj'], errors='coerce').fillna(0)
                results[str(category)]['avg_injuries'] = float(injuries.mean())

            # Average property loss by category
            if 'prop_loss' in cat_df.columns:
                losses = pd.to_numeric(cat_df['prop_loss'], errors='coerce').fillna(0)
                results[str(category)]['avg_property_loss'] = float(losses.mean())

        logger.info(f"Comparative analysis complete for {len(categories)} categories")

        return results

    def _assign_regions(self, states: pd.Series) -> pd.Series:
        """
        Assign US census regions to states.

        Args:
            states: Series of state abbreviations

        Returns:
            Series of region names
        """
        region_map = {
            # Northeast
            'CT': 'Northeast', 'ME': 'Northeast', 'MA': 'Northeast', 'NH': 'Northeast',
            'RI': 'Northeast', 'VT': 'Northeast', 'NJ': 'Northeast', 'NY': 'Northeast',
            'PA': 'Northeast',
            # Midwest
            'IL': 'Midwest', 'IN': 'Midwest', 'MI': 'Midwest', 'OH': 'Midwest',
            'WI': 'Midwest', 'IA': 'Midwest', 'KS': 'Midwest', 'MN': 'Midwest',
            'MO': 'Midwest', 'NE': 'Midwest', 'ND': 'Midwest', 'SD': 'Midwest',
            # South
            'DE': 'South', 'FL': 'South', 'GA': 'South', 'MD': 'South',
            'NC': 'South', 'SC': 'South', 'VA': 'South', 'WV': 'South',
            'AL': 'South', 'KY': 'South', 'MS': 'South', 'TN': 'South',
            'AR': 'South', 'LA': 'South', 'OK': 'South', 'TX': 'South',
            # West
            'AZ': 'West', 'CO': 'West', 'ID': 'West', 'MT': 'West',
            'NV': 'West', 'NM': 'West', 'UT': 'West', 'WY': 'West',
            'AK': 'West', 'CA': 'West', 'HI': 'West', 'OR': 'West', 'WA': 'West'
        }

        return states.map(region_map).fillna('Unknown')

    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a comprehensive summary report.

        Args:
            df: DataFrame containing incident data

        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Generating comprehensive summary report...")

        summary = {
            'metadata': {
                'total_incidents': len(df),
                'date_range': self._get_date_range(df),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'temporal': self.temporal_analysis(df),
            'geographic': self.geographic_analysis(df),
            'casualties': self.casualty_analysis(df),
            'property_loss': self.property_loss_analysis(df),
            'characteristics': self.incident_characteristics(df),
            'comparative': self.comparative_analysis(df)
        }

        logger.info("Summary report generation complete")

        return summary

    def _get_date_range(self, df: pd.DataFrame) -> Dict:
        """Get the date range of incidents in the dataset."""
        if 'inc_date' not in df.columns or df.empty:
            return {}

        dates = pd.to_datetime(df['inc_date'], errors='coerce').dropna()

        if dates.empty:
            return {}

        return {
            'start_date': dates.min().isoformat(),
            'end_date': dates.max().isoformat(),
            'span_days': (dates.max() - dates.min()).days
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    from data_loader import NFIRSDataLoader, create_sample_data
    from filters import NFIRSIncidentFilter

    # Create and load sample data
    create_sample_data()
    loader = NFIRSDataLoader()
    modules = loader.load_all_modules()
    merged_data = loader.merge_modules(modules)

    # Filter incidents
    filter_obj = NFIRSIncidentFilter()
    filtered_data = filter_obj.filter_all_incidents(merged_data)
    filtered_data = filter_obj.add_subcategories(filtered_data)

    # Analyze
    analyzer = NFIRSAnalyzer()
    summary = analyzer.generate_summary_report(filtered_data)

    print("\n=== Analysis Summary ===")
    print(f"Total incidents: {summary['metadata']['total_incidents']}")
    print(f"Temporal trends: {summary['temporal'].get('yearly', {})}")
    print(f"Geographic distribution: {summary['geographic'].get('top_10_states', {})}")
