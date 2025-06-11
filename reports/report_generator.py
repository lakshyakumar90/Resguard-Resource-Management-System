"""
Report Generator Module

This module provides functionality to generate HTML reports containing
resource usage data, charts, and tabular information.
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pandas as pd
import base64
from io import BytesIO

from core.resource_manager import ResourceManager
from utils.system_monitor import SystemMonitor
from utils.config import Config


class ReportGenerator:
    """
    Generates comprehensive HTML reports with resource usage data and visualizations.
    """
    
    def __init__(self, resource_manager: ResourceManager, system_monitor: SystemMonitor, config: Config):
        """
        Initialize the report generator.
        
        Args:
            resource_manager: Resource manager instance
            system_monitor: System monitor instance
            config: Configuration object
        """
        self.resource_manager = resource_manager
        self.system_monitor = system_monitor
        self.config = config
        
        # Ensure reports directory exists
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def generate_report(self, time_range: int = 3600, include_charts: bool = True, 
                       include_tables: bool = True, report_name: str = "resource_usage_report") -> Optional[str]:
        """
        Generate a comprehensive resource usage report.
        
        Args:
            time_range: Time range in seconds for historical data
            include_charts: Whether to include charts in the report
            include_tables: Whether to include tables in the report
            report_name: Base name for the report file
            
        Returns:
            str: Path to the generated report file, or None if generation failed
        """
        try:
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{report_name}_{timestamp}.html"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            # Collect data
            system_state = self.resource_manager.get_system_state()
            system_metrics = self.system_monitor.get_metrics()
            system_history = self.system_monitor.get_history()
            processes = self.system_monitor.get_processes()
            
            # Generate report content
            html_content = self._generate_html_report(
                system_state, system_metrics, system_history, processes,
                time_range, include_charts, include_tables
            )
            
            # Write report to file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return report_path
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def _generate_html_report(self, system_state: Dict, system_metrics: Dict, 
                             system_history: Dict, processes: List[Dict],
                             time_range: int, include_charts: bool, include_tables: bool) -> str:
        """
        Generate the HTML content for the report.
        """
        # Load HTML template
        template_path = os.path.join(os.path.dirname(__file__), "templates", "report_template.html")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            template = self._get_default_template()
        
        # Generate report sections
        report_data = {
            'title': 'ResGuard Resource Usage Report',
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'time_range_hours': time_range / 3600,
            'summary': self._generate_summary(system_state, system_metrics),
            'charts': self._generate_charts(system_history, time_range) if include_charts else "",
            'tables': self._generate_tables(system_state, processes) if include_tables else "",
            'resource_allocation': self._generate_resource_allocation_section(system_state),
            'request_history': self._generate_request_history_section(system_state)
        }
        
        # Replace placeholders in template
        html_content = template
        for key, value in report_data.items():
            html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            
        return html_content
    
    def _generate_summary(self, system_state: Dict, system_metrics: Dict) -> str:
        """Generate summary statistics section."""
        total_resources = self.config.get("resources")
        available = system_state["available"]
        
        summary_html = """
        <div class="row">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">CPU Usage</h5>
                        <h3 class="text-primary">{cpu_percent:.1f}%</h3>
                        <p class="text-muted">{cpu_used}/{cpu_total} allocated</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Memory Usage</h5>
                        <h3 class="text-success">{mem_percent:.1f}%</h3>
                        <p class="text-muted">{mem_used}/{mem_total} MB allocated</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Disk Usage</h5>
                        <h3 class="text-warning">{disk_percent:.1f}%</h3>
                        <p class="text-muted">{disk_used}/{disk_total} MB allocated</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Network Usage</h5>
                        <h3 class="text-info">{net_percent:.1f}%</h3>
                        <p class="text-muted">{net_used}/{net_total} Mbps allocated</p>
                    </div>
                </div>
            </div>
        </div>
        """.format(
            cpu_percent=system_metrics["cpu"]["percent"],
            cpu_used=total_resources["cpu"] - available["cpu"],
            cpu_total=total_resources["cpu"],
            mem_percent=system_metrics["memory"]["percent"],
            mem_used=total_resources["memory"] - available["memory"],
            mem_total=total_resources["memory"],
            disk_percent=system_metrics["disk"]["percent"],
            disk_used=total_resources["disk"] - available["disk"],
            disk_total=total_resources["disk"],
            net_percent=(total_resources["network"] - available["network"]) / total_resources["network"] * 100,
            net_used=total_resources["network"] - available["network"],
            net_total=total_resources["network"]
        )
        
        return summary_html
    
    def _generate_charts(self, system_history: Dict, time_range: int) -> str:
        """Generate charts section with embedded images."""
        charts_html = "<h3>Resource Usage Over Time</h3>\n"
        
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('System Resource Usage History', fontsize=16)
            
            # Get timestamps and limit to time range
            timestamps = system_history.get("timestamps", [])
            if not timestamps:
                return "<p>No historical data available for charts.</p>"
            
            # Convert timestamps to datetime objects
            current_time = time.time()
            start_time = current_time - time_range
            
            # Filter data within time range
            filtered_indices = [i for i, ts in enumerate(timestamps) if ts >= start_time]
            if not filtered_indices:
                return "<p>No data available for the selected time range.</p>"
            
            filtered_timestamps = [datetime.fromtimestamp(timestamps[i]) for i in filtered_indices]
            
            # CPU Usage Chart
            cpu_data = [system_history["cpu"][i] for i in filtered_indices]
            axes[0, 0].plot(filtered_timestamps, cpu_data, 'b-', linewidth=2)
            axes[0, 0].set_title('CPU Usage (%)')
            axes[0, 0].set_ylabel('Percentage')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Memory Usage Chart
            memory_data = [system_history["memory"][i] for i in filtered_indices]
            axes[0, 1].plot(filtered_timestamps, memory_data, 'g-', linewidth=2)
            axes[0, 1].set_title('Memory Usage (%)')
            axes[0, 1].set_ylabel('Percentage')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Disk Usage Chart
            disk_data = [system_history["disk"][i] for i in filtered_indices]
            axes[1, 0].plot(filtered_timestamps, disk_data, 'r-', linewidth=2)
            axes[1, 0].set_title('Disk Usage (%)')
            axes[1, 0].set_ylabel('Percentage')
            axes[1, 0].grid(True, alpha=0.3)
            
            # Network Usage Chart (bytes sent/received)
            network_data = system_history.get("network", [])
            if network_data and filtered_indices:
                net_sent = [network_data[i]["sent"] / (1024*1024) for i in filtered_indices]  # Convert to MB
                net_recv = [network_data[i]["recv"] / (1024*1024) for i in filtered_indices]  # Convert to MB
                axes[1, 1].plot(filtered_timestamps, net_sent, 'orange', label='Sent (MB)', linewidth=2)
                axes[1, 1].plot(filtered_timestamps, net_recv, 'purple', label='Received (MB)', linewidth=2)
                axes[1, 1].set_title('Network Usage')
                axes[1, 1].set_ylabel('MB')
                axes[1, 1].legend()
                axes[1, 1].grid(True, alpha=0.3)
            
            # Format x-axis for all subplots
            for ax in axes.flat:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Convert plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            charts_html += f'<img src="data:image/png;base64,{image_base64}" class="img-fluid" alt="Resource Usage Charts">\n'
            
        except Exception as e:
            charts_html += f"<p>Error generating charts: {e}</p>"
        
        return charts_html

    def _generate_tables(self, system_state: Dict, processes: List[Dict]) -> str:
        """Generate tables section."""
        tables_html = "<h3>System Information Tables</h3>\n"

        # Current Processes Table
        tables_html += """
        <h4>Top Processes by CPU Usage</h4>
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead class="thead-dark">
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>CPU %</th>
                        <th>Memory %</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Add top 10 processes
        for proc in processes[:10]:
            tables_html += f"""
                    <tr>
                        <td>{proc.get('pid', 'N/A')}</td>
                        <td>{proc.get('name', 'N/A')[:30]}</td>
                        <td>{proc.get('cpu_percent', 0):.1f}</td>
                        <td>{proc.get('memory_percent', 0):.1f}</td>
                        <td>{proc.get('status', 'N/A')}</td>
                    </tr>
            """

        tables_html += """
                </tbody>
            </table>
        </div>
        """

        return tables_html

    def _generate_resource_allocation_section(self, system_state: Dict) -> str:
        """Generate resource allocation section."""
        allocation_html = """
        <h3>Current Resource Allocations</h3>
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead class="thead-dark">
                    <tr>
                        <th>Process ID</th>
                        <th>CPU</th>
                        <th>Memory</th>
                        <th>Disk</th>
                        <th>Network</th>
                        <th>Status</th>
                        <th>Registered At</th>
                    </tr>
                </thead>
                <tbody>
        """

        allocations = system_state.get("allocation", {})
        process_info = system_state.get("process_info", {})

        for pid, allocation in allocations.items():
            info = process_info.get(pid, {})
            registered_time = info.get("registered_at", 0)
            registered_str = datetime.fromtimestamp(registered_time).strftime("%Y-%m-%d %H:%M:%S") if registered_time else "N/A"

            allocation_html += f"""
                    <tr>
                        <td>{pid}</td>
                        <td>{allocation.get('cpu', 0)}</td>
                        <td>{allocation.get('memory', 0)}</td>
                        <td>{allocation.get('disk', 0)}</td>
                        <td>{allocation.get('network', 0)}</td>
                        <td>{info.get('status', 'unknown')}</td>
                        <td>{registered_str}</td>
                    </tr>
            """

        allocation_html += """
                </tbody>
            </table>
        </div>
        """

        if not allocations:
            allocation_html += "<p>No active resource allocations.</p>"

        return allocation_html

    def _generate_request_history_section(self, system_state: Dict) -> str:
        """Generate request history section."""
        history_html = """
        <h3>Recent Resource Requests</h3>
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead class="thead-dark">
                    <tr>
                        <th>Timestamp</th>
                        <th>Type</th>
                        <th>Process ID</th>
                        <th>Resources</th>
                        <th>Success</th>
                    </tr>
                </thead>
                <tbody>
        """

        request_history = system_state.get("request_history", [])

        # Show last 20 requests
        for request in request_history[-20:]:
            timestamp_str = datetime.fromtimestamp(request.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
            resources_str = ", ".join([f"{k}:{v}" for k, v in request.get("resources", {}).items()])
            success_str = "✓" if request.get("success", False) else "✗"
            success_class = "text-success" if request.get("success", False) else "text-danger"

            history_html += f"""
                    <tr>
                        <td>{timestamp_str}</td>
                        <td>{request.get('type', 'unknown')}</td>
                        <td>{request.get('process_id', 'N/A')}</td>
                        <td>{resources_str}</td>
                        <td class="{success_class}">{success_str}</td>
                    </tr>
            """

        history_html += """
                </tbody>
            </table>
        </div>
        """

        if not request_history:
            history_html += "<p>No request history available.</p>"

        return history_html

    def _get_default_template(self) -> str:
        """Get default HTML template if template file doesn't exist."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }
        .card { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 1rem; }
        .table th { background-color: #343a40; color: white; }
        .footer { background-color: #f8f9fa; padding: 1rem 0; margin-top: 2rem; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1 class="display-4">{{title}}</h1>
            <p class="lead">Generated on {{generation_time}}</p>
            <p>Time Range: {{time_range_hours}} hours</p>
        </div>
    </div>

    <div class="container mt-4">
        <section class="mb-5">
            <h2>Summary</h2>
            {{summary}}
        </section>

        <section class="mb-5">
            {{charts}}
        </section>

        <section class="mb-5">
            {{resource_allocation}}
        </section>

        <section class="mb-5">
            {{request_history}}
        </section>

        <section class="mb-5">
            {{tables}}
        </section>
    </div>

    <div class="footer">
        <div class="container text-center">
            <p class="text-muted">Generated by ResGuard Resource Management System</p>
        </div>
    </div>
</body>
</html>
        """
