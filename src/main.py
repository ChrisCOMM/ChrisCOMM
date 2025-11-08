#!/usr/bin/env python3
"""
NFIRS Solar Panel & Lithium-Ion Battery Fire Analysis

Main workflow orchestrator for analyzing NFIRS fire incident data.
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from data_loader import NFIRSDataLoader, create_sample_data
from filters import NFIRSIncidentFilter
from analyzers import NFIRSAnalyzer
from reporters import NFIRSReporter


def setup_logging(log_level: str = "INFO"):
    """Configure logging for the workflow."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/nfirs_workflow.log')
        ]
    )


@click.group()
@click.option('--log-level', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              help='Set logging level')
def cli(log_level):
    """NFIRS Solar Panel & Lithium-Ion Battery Fire Analysis Tool"""
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    setup_logging(log_level)


@cli.command()
@click.option('--output-dir', default='data', help='Output directory for sample data')
def create_sample(output_dir):
    """Create sample NFIRS data for testing."""
    logger = logging.getLogger(__name__)
    logger.info(f"Creating sample data in {output_dir}")

    create_sample_data(output_dir)

    logger.info("Sample data created successfully")
    click.echo(f"✓ Sample data created in {output_dir}/")


@cli.command()
@click.option('--input', '-i', 'input_path', help='Path to NFIRS basic module CSV file')
@click.option('--type', '-t', 'incident_type',
              type=click.Choice(['solar', 'battery', 'all']),
              default='all',
              help='Type of incidents to filter')
@click.option('--year', '-y', type=int, help='Filter by specific year')
@click.option('--output', '-o', 'output_dir', default='reports',
              help='Output directory for reports')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['html', 'csv', 'json', 'txt', 'all']),
              default='all',
              help='Report format')
def analyze(input_path, incident_type, year, output_dir, output_format):
    """
    Analyze NFIRS data for solar panel and battery incidents.

    Example:
        python main.py analyze --input data/basicincident.csv --type all
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Starting NFIRS Analysis Workflow")
    logger.info("=" * 80)

    # Step 1: Load data
    click.echo("📂 Loading NFIRS data...")
    loader = NFIRSDataLoader()

    if input_path:
        basic_data = loader.load_basic_module(input_path)
        fire_data = loader.load_fire_module(input_path.replace('basic', 'fire'))
        modules = {'basic': basic_data, 'fire': fire_data}
    else:
        modules = loader.load_all_modules()

    merged_data = loader.merge_modules(modules)

    if merged_data.empty:
        click.echo("❌ No data loaded. Please check your data files.")
        return

    click.echo(f"✓ Loaded {len(merged_data):,} total incidents")

    # Filter by year if specified
    if year and 'inc_year' in merged_data.columns:
        merged_data = merged_data[merged_data['inc_year'] == year]
        click.echo(f"✓ Filtered to year {year}: {len(merged_data):,} incidents")

    # Step 2: Filter incidents
    click.echo(f"\n🔍 Filtering for {incident_type} incidents...")
    incident_filter = NFIRSIncidentFilter()

    if incident_type == 'solar':
        filtered_data = incident_filter.filter_solar_incidents(merged_data)
    elif incident_type == 'battery':
        filtered_data = incident_filter.filter_battery_incidents(merged_data)
    else:  # all
        filtered_data = incident_filter.filter_all_incidents(merged_data)

    # Add subcategories
    filtered_data = incident_filter.add_subcategories(filtered_data)

    if filtered_data.empty:
        click.echo("❌ No matching incidents found.")
        return

    click.echo(f"✓ Found {len(filtered_data):,} matching incidents")

    # Print filter statistics
    stats = incident_filter.get_filter_statistics(filtered_data)
    if stats.get('by_category'):
        click.echo("\nIncidents by category:")
        for category, count in stats['by_category'].items():
            click.echo(f"  • {category}: {count:,}")

    # Step 3: Analyze data
    click.echo("\n📊 Analyzing incidents...")
    analyzer = NFIRSAnalyzer()
    analysis = analyzer.generate_summary_report(filtered_data)

    click.echo(f"✓ Analysis complete")

    # Print key findings
    click.echo("\n=== Key Findings ===")
    metadata = analysis.get('metadata', {})
    casualties = analysis.get('casualties', {})
    prop_loss = analysis.get('property_loss', {})

    click.echo(f"Total Incidents: {metadata.get('total_incidents', 0):,}")
    click.echo(f"Deaths: {casualties.get('total_deaths', 0)}")
    click.echo(f"Injuries: {casualties.get('total_injuries', 0)}")
    click.echo(f"Property Loss: ${prop_loss.get('total_property_loss', 0):,.2f}")

    # Step 4: Generate reports
    click.echo(f"\n📝 Generating {output_format} report(s)...")
    reporter = NFIRSReporter(output_dir)

    if output_format == 'all':
        report_paths = reporter.generate_all_reports(filtered_data, analysis)
    else:
        report_paths = {}
        if output_format == 'html':
            report_paths['html'] = reporter.generate_html_report(analysis)
        elif output_format == 'csv':
            report_paths['csv'] = reporter.generate_csv_report(filtered_data)
        elif output_format == 'json':
            report_paths['json'] = reporter.generate_json_report(analysis)
        elif output_format == 'txt':
            report_paths['txt'] = reporter.generate_summary_text(analysis)

    click.echo("\n✓ Reports generated:")
    for report_type, path in report_paths.items():
        click.echo(f"  • {report_type.upper()}: {path}")

    click.echo("\n" + "=" * 80)
    click.echo("Analysis complete!")
    click.echo("=" * 80)


@cli.command()
@click.option('--input', '-i', 'input_path', required=True,
              help='Path to NFIRS basic module CSV file')
def stats(input_path):
    """Display statistics about NFIRS data file."""
    logger = logging.getLogger(__name__)

    click.echo(f"📊 Analyzing {input_path}...")

    loader = NFIRSDataLoader()
    data = loader.load_basic_module(input_path)

    if data.empty:
        click.echo("❌ Could not load data file")
        return

    click.echo(f"\n=== Data Statistics ===")
    click.echo(f"Total records: {len(data):,}")
    click.echo(f"Columns: {len(data.columns)}")
    click.echo(f"Memory usage: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    if 'inc_year' in data.columns:
        year_counts = data['inc_year'].value_counts().sort_index()
        click.echo(f"\nRecords by year:")
        for year, count in year_counts.items():
            click.echo(f"  {year}: {count:,}")

    if 'inc_type' in data.columns:
        type_counts = data['inc_type'].value_counts()
        click.echo(f"\nTop 10 incident types:")
        for inc_type, count in type_counts.head(10).items():
            click.echo(f"  {inc_type}: {count:,}")

    if 'state' in data.columns:
        state_counts = data['state'].value_counts()
        click.echo(f"\nTop 10 states:")
        for state, count in state_counts.head(10).items():
            click.echo(f"  {state}: {count:,}")


@cli.command()
@click.option('--type', '-t', 'incident_type',
              type=click.Choice(['solar', 'battery', 'all']),
              default='all',
              help='Type of incidents to check')
def check_codes(incident_type):
    """Display NFIRS codes used for filtering."""
    from filters import NFIRSIncidentFilter

    filter_obj = NFIRSIncidentFilter()

    click.echo("=== NFIRS Codes Configuration ===\n")

    if incident_type in ['solar', 'all']:
        click.echo("Solar Panel Equipment Codes:")
        for code in sorted(filter_obj.solar_equipment_codes):
            click.echo(f"  • {code}")

        click.echo("\nSolar Heat Source Codes:")
        for code in sorted(filter_obj.solar_heat_sources):
            click.echo(f"  • {code}")

        click.echo("\nSolar Keywords:")
        for keyword in filter_obj.solar_keywords:
            click.echo(f"  • {keyword}")

    if incident_type in ['battery', 'all']:
        click.echo("\nBattery Equipment Codes:")
        for code in sorted(filter_obj.battery_equipment_codes):
            click.echo(f"  • {code}")

        click.echo("\nBattery Heat Source Codes:")
        for code in sorted(filter_obj.battery_heat_sources):
            click.echo(f"  • {code}")

        click.echo("\nBattery Keywords:")
        for keyword in filter_obj.battery_keywords:
            click.echo(f"  • {keyword}")


if __name__ == "__main__":
    cli()
