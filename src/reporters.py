"""
NFIRS Report Generation Module

Generates reports and visualizations from analyzed NFIRS data.
"""

import pandas as pd
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)


class NFIRSReporter:
    """Generates reports from NFIRS analysis results."""

    def __init__(self, output_dir: str = "reports",
                 config_path: str = "config/workflow_config.yml"):
        """
        Initialize the reporter.

        Args:
            output_dir: Directory to save reports
            config_path: Path to workflow configuration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config(config_path)
        self.report_config = self.config.get('reporting', {})

        # Create timestamped subdirectory if configured
        if self.config.get('output', {}).get('use_timestamps', True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_dir = self.output_dir / timestamp
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}. Using defaults.")
            return {}

    def generate_html_report(self, analysis: Dict, filename: str = "report.html") -> str:
        """
        Generate an HTML report.

        Args:
            analysis: Analysis results dictionary
            filename: Output filename

        Returns:
            Path to generated report
        """
        logger.info("Generating HTML report...")

        output_path = self.output_dir / filename

        html_content = self._build_html_report(analysis)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML report saved to {output_path}")
        return str(output_path)

    def generate_csv_report(self, df: pd.DataFrame, filename: str = "incidents.csv") -> str:
        """
        Generate a CSV report.

        Args:
            df: DataFrame containing incident data
            filename: Output filename

        Returns:
            Path to generated report
        """
        logger.info("Generating CSV report...")

        output_path = self.output_dir / filename

        df.to_csv(output_path, index=False)

        logger.info(f"CSV report saved to {output_path}")
        return str(output_path)

    def generate_json_report(self, analysis: Dict, filename: str = "analysis.json") -> str:
        """
        Generate a JSON report.

        Args:
            analysis: Analysis results dictionary
            filename: Output filename

        Returns:
            Path to generated report
        """
        logger.info("Generating JSON report...")

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"JSON report saved to {output_path}")
        return str(output_path)

    def generate_summary_text(self, analysis: Dict, filename: str = "summary.txt") -> str:
        """
        Generate a plain text summary report.

        Args:
            analysis: Analysis results dictionary
            filename: Output filename

        Returns:
            Path to generated report
        """
        logger.info("Generating text summary...")

        output_path = self.output_dir / filename

        summary_text = self._build_text_summary(analysis)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)

        logger.info(f"Text summary saved to {output_path}")
        return str(output_path)

    def _build_html_report(self, analysis: Dict) -> str:
        """Build HTML report content."""

        metadata = analysis.get('metadata', {})
        temporal = analysis.get('temporal', {})
        geographic = analysis.get('geographic', {})
        casualties = analysis.get('casualties', {})
        property_loss = analysis.get('property_loss', {})
        characteristics = analysis.get('characteristics', {})

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFIRS Solar Panel & Lithium Battery Fire Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .metric {{
            display: inline-block;
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            min-width: 200px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NFIRS Fire Incident Analysis Report</h1>
        <h3>Solar Panels & Lithium-Ion Batteries</h3>
        <p>Generated: {metadata.get('analysis_timestamp', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="metric-value">{metadata.get('total_incidents', 0):,}</div>
            <div class="metric-label">Total Incidents</div>
        </div>
        <div class="metric">
            <div class="metric-value">{casualties.get('total_deaths', 0)}</div>
            <div class="metric-label">Total Deaths</div>
        </div>
        <div class="metric">
            <div class="metric-value">{casualties.get('total_injuries', 0)}</div>
            <div class="metric-label">Total Injuries</div>
        </div>
        <div class="metric">
            <div class="metric-value">${property_loss.get('total_property_loss', 0):,.0f}</div>
            <div class="metric-label">Total Property Loss</div>
        </div>
    </div>

    <div class="section">
        <h2>Temporal Analysis</h2>
        <h3>Incidents by Year</h3>
        <table>
            <tr>
                <th>Year</th>
                <th>Incidents</th>
                <th>Growth Rate</th>
            </tr>
            {self._build_yearly_table(temporal.get('yearly', {}), temporal.get('yearly_growth_rate', {}))}
        </table>
    </div>

    <div class="section">
        <h2>Geographic Distribution</h2>
        <h3>Top 10 States</h3>
        <table>
            <tr>
                <th>State</th>
                <th>Incidents</th>
                <th>Percentage</th>
            </tr>
            {self._build_state_table(geographic.get('top_10_states', {}), metadata.get('total_incidents', 1))}
        </table>
    </div>

    <div class="section">
        <h2>Incident Characteristics</h2>
        <h3>By Category</h3>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
            </tr>
            {self._build_simple_table(characteristics.get('by_category', {}))}
        </table>

        <h3>By Subcategory</h3>
        <table>
            <tr>
                <th>Subcategory</th>
                <th>Count</th>
            </tr>
            {self._build_simple_table(characteristics.get('by_subcategory', {}))}
        </table>
    </div>

    <div class="section">
        <h2>Casualty Analysis</h2>
        <p><strong>Incidents with Casualties:</strong> {casualties.get('incidents_with_casualties', 0)}</p>
        <p><strong>Casualty Rate:</strong> {casualties.get('casualty_rate', 0):.2f}%</p>

        <h3>Breakdown</h3>
        <ul>
            <li>Firefighter Deaths: {casualties.get('firefighter_deaths', 0)}</li>
            <li>Firefighter Injuries: {casualties.get('firefighter_injuries', 0)}</li>
            <li>Civilian Deaths: {casualties.get('civilian_deaths', 0)}</li>
            <li>Civilian Injuries: {casualties.get('civilian_injuries', 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2>Property Loss Analysis</h2>
        <h3>Loss Distribution</h3>
        <table>
            <tr>
                <th>Loss Range</th>
                <th>Incidents</th>
            </tr>
            {self._build_loss_distribution_table(property_loss.get('loss_distribution', {}))}
        </table>

        <p><strong>Mean Property Loss:</strong> ${property_loss.get('prop_loss_mean', 0):,.2f}</p>
        <p><strong>Median Property Loss:</strong> ${property_loss.get('prop_loss_median', 0):,.2f}</p>
        <p><strong>Maximum Property Loss:</strong> ${property_loss.get('prop_loss_max', 0):,.2f}</p>
    </div>

    <div class="footer">
        <p>This report was automatically generated by the NFIRS Analysis Workflow</p>
        <p>Data source: National Fire Incident Reporting System (NFIRS)</p>
    </div>
</body>
</html>
"""
        return html

    def _build_yearly_table(self, yearly: Dict, growth: Dict) -> str:
        """Build yearly trends table rows."""
        rows = []
        for year in sorted(yearly.keys()):
            count = yearly[year]
            growth_rate = growth.get(year, 0)
            growth_str = f"{growth_rate:+.1f}%" if growth_rate else "N/A"
            rows.append(f"<tr><td>{year}</td><td>{count:,}</td><td>{growth_str}</td></tr>")
        return "\n".join(rows)

    def _build_state_table(self, states: Dict, total: int) -> str:
        """Build state distribution table rows."""
        rows = []
        for state, count in list(states.items())[:10]:
            percentage = (count / total * 100) if total > 0 else 0
            rows.append(f"<tr><td>{state}</td><td>{count:,}</td><td>{percentage:.1f}%</td></tr>")
        return "\n".join(rows)

    def _build_simple_table(self, data: Dict) -> str:
        """Build simple two-column table rows."""
        rows = []
        for key, value in data.items():
            rows.append(f"<tr><td>{key}</td><td>{value:,}</td></tr>")
        return "\n".join(rows)

    def _build_loss_distribution_table(self, distribution: Dict) -> str:
        """Build property loss distribution table."""
        ranges = {
            'under_10k': 'Under $10,000',
            '10k_to_100k': '$10,000 - $100,000',
            '100k_to_1m': '$100,000 - $1,000,000',
            'over_1m': 'Over $1,000,000'
        }

        rows = []
        for key, label in ranges.items():
            count = distribution.get(key, 0)
            rows.append(f"<tr><td>{label}</td><td>{count:,}</td></tr>")
        return "\n".join(rows)

    def _build_text_summary(self, analysis: Dict) -> str:
        """Build plain text summary."""

        metadata = analysis.get('metadata', {})
        temporal = analysis.get('temporal', {})
        geographic = analysis.get('geographic', {})
        casualties = analysis.get('casualties', {})
        characteristics = analysis.get('characteristics', {})

        text = f"""
================================================================================
NFIRS FIRE INCIDENT ANALYSIS REPORT
Solar Panels & Lithium-Ion Batteries
================================================================================

Generated: {metadata.get('analysis_timestamp', 'N/A')}

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Total Incidents:          {metadata.get('total_incidents', 0):,}
Total Deaths:             {casualties.get('total_deaths', 0)}
Total Injuries:           {casualties.get('total_injuries', 0)}
Total Property Loss:      ${analysis.get('property_loss', {}).get('total_property_loss', 0):,.2f}

TEMPORAL TRENDS
--------------------------------------------------------------------------------
Incidents by Year:
"""

        # Add yearly data
        yearly = temporal.get('yearly', {})
        for year in sorted(yearly.keys()):
            text += f"  {year}: {yearly[year]:,} incidents\n"

        text += "\nGEOGRAPHIC DISTRIBUTION\n"
        text += "-" * 80 + "\n"
        text += "Top 10 States:\n"

        # Add state data
        top_states = geographic.get('top_10_states', {})
        for i, (state, count) in enumerate(list(top_states.items())[:10], 1):
            percentage = (count / metadata.get('total_incidents', 1) * 100)
            text += f"  {i}. {state}: {count:,} incidents ({percentage:.1f}%)\n"

        text += "\nINCIDENT CATEGORIES\n"
        text += "-" * 80 + "\n"

        categories = characteristics.get('by_category', {})
        for category, count in categories.items():
            text += f"  {category}: {count:,}\n"

        text += "\nSUBCATEGORIES\n"
        text += "-" * 80 + "\n"

        subcategories = characteristics.get('by_subcategory', {})
        for subcat, count in subcategories.items():
            text += f"  {subcat}: {count:,}\n"

        text += "\n" + "=" * 80 + "\n"
        text += "End of Report\n"
        text += "=" * 80 + "\n"

        return text

    def generate_all_reports(self, df: pd.DataFrame, analysis: Dict) -> Dict[str, str]:
        """
        Generate all configured report formats.

        Args:
            df: DataFrame containing incident data
            analysis: Analysis results dictionary

        Returns:
            Dictionary mapping report type to file path
        """
        logger.info("Generating all reports...")

        reports = {}
        formats = self.report_config.get('formats', ['html', 'csv', 'json'])

        if 'html' in formats:
            reports['html'] = self.generate_html_report(analysis)

        if 'csv' in formats:
            reports['csv'] = self.generate_csv_report(df)

        if 'json' in formats:
            reports['json'] = self.generate_json_report(analysis)

        if 'txt' in formats or 'text' in formats:
            reports['txt'] = self.generate_summary_text(analysis)

        logger.info(f"Generated {len(reports)} reports in {self.output_dir}")

        return reports


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test report generation
    from data_loader import NFIRSDataLoader, create_sample_data
    from filters import NFIRSIncidentFilter
    from analyzers import NFIRSAnalyzer

    # Create and process sample data
    create_sample_data()
    loader = NFIRSDataLoader()
    modules = loader.load_all_modules()
    merged_data = loader.merge_modules(modules)

    # Filter and analyze
    filter_obj = NFIRSIncidentFilter()
    filtered_data = filter_obj.filter_all_incidents(merged_data)
    filtered_data = filter_obj.add_subcategories(filtered_data)

    analyzer = NFIRSAnalyzer()
    analysis = analyzer.generate_summary_report(filtered_data)

    # Generate reports
    reporter = NFIRSReporter()
    report_paths = reporter.generate_all_reports(filtered_data, analysis)

    print("\n=== Reports Generated ===")
    for report_type, path in report_paths.items():
        print(f"{report_type.upper()}: {path}")
