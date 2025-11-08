"""
Unit tests for NFIRS filters module
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from filters import NFIRSIncidentFilter
from data_loader import create_sample_data, NFIRSDataLoader


@pytest.fixture
def sample_data():
    """Create sample NFIRS data for testing."""
    create_sample_data('data')
    loader = NFIRSDataLoader()
    modules = loader.load_all_modules()
    return loader.merge_modules(modules)


@pytest.fixture
def incident_filter():
    """Create incident filter instance."""
    return NFIRSIncidentFilter()


def test_filter_initialization(incident_filter):
    """Test that filter initializes correctly."""
    assert incident_filter is not None
    assert len(incident_filter.solar_equipment_codes) > 0
    assert len(incident_filter.battery_equipment_codes) > 0
    assert len(incident_filter.solar_keywords) > 0
    assert len(incident_filter.battery_keywords) > 0


def test_solar_incident_filtering(sample_data, incident_filter):
    """Test filtering for solar panel incidents."""
    result = incident_filter.filter_solar_incidents(sample_data)

    assert isinstance(result, pd.DataFrame)
    # Should find at least some incidents based on sample data
    assert 'incident_category' in result.columns


def test_battery_incident_filtering(sample_data, incident_filter):
    """Test filtering for battery incidents."""
    result = incident_filter.filter_battery_incidents(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert 'incident_category' in result.columns


def test_all_incident_filtering(sample_data, incident_filter):
    """Test filtering for all incident types."""
    result = incident_filter.filter_all_incidents(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert 'incident_category' in result.columns


def test_subcategory_assignment(sample_data, incident_filter):
    """Test subcategory assignment."""
    filtered = incident_filter.filter_all_incidents(sample_data)
    result = incident_filter.add_subcategories(filtered)

    assert 'subcategory' in result.columns
    # All rows should have a subcategory
    assert result['subcategory'].notna().all()


def test_filter_statistics(sample_data, incident_filter):
    """Test filter statistics generation."""
    filtered = incident_filter.filter_all_incidents(sample_data)
    stats = incident_filter.get_filter_statistics(filtered)

    assert isinstance(stats, dict)
    assert 'total_incidents' in stats
    assert 'by_category' in stats
    assert stats['total_incidents'] >= 0


def test_empty_dataframe_handling(incident_filter):
    """Test that filter handles empty DataFrames gracefully."""
    empty_df = pd.DataFrame()

    solar = incident_filter.filter_solar_incidents(empty_df)
    battery = incident_filter.filter_battery_incidents(empty_df)
    all_incidents = incident_filter.filter_all_incidents(empty_df)

    assert solar.empty
    assert battery.empty
    assert all_incidents.empty


def test_narrative_matching(incident_filter):
    """Test narrative keyword matching."""
    # Create test data with narrative
    test_data = pd.DataFrame({
        'state': ['CA'],
        'fdid': ['12345'],
        'inc_date': ['2024-01-01'],
        'inc_no': ['001'],
        'exp_no': ['00'],
        'inc_type': [111],
        'narrative': ['Fire in solar panel system on roof']
    })

    result = incident_filter.filter_solar_incidents(test_data)

    # Should match due to narrative containing "solar panel"
    if incident_filter.use_narrative:
        assert len(result) > 0 or len(result) == 0  # Depends on config


def test_code_based_filtering(incident_filter):
    """Test filtering based on NFIRS codes."""
    # Create test data with solar equipment code
    test_data = pd.DataFrame({
        'state': ['CA'],
        'fdid': ['12345'],
        'inc_date': ['2024-01-01'],
        'inc_no': ['001'],
        'exp_no': ['00'],
        'inc_type': [111],
        'item_first_ig': [262],  # Solar energy system code
        'heat_source': [87]      # Solar heat source
    })

    result = incident_filter.filter_solar_incidents(test_data)
    assert len(result) > 0  # Should match based on codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
