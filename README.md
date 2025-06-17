# ResGuard: Dynamic Resource Management System

A streamlined system for dynamically allocating computing resources (e.g., memory, CPU, storage) using the Banker's Algorithm to prevent deadlocks, optimize utilization, and provide real-time monitoring with minimal console output.

![ResGuard Dashboard](docs/images/dashboard.png)

## Project Overview

**Motivation**: Resource competition in computing causes bottlenecks and deadlocks, contributing to ~25% of system slowdowns (TechSys Reports, 2024). ResGuard ensures efficient resource allocation, prevents deadlocks, and enhances system reliability.

**Objectives**:
1. Prevent deadlocks while maximizing resource use (up to 90% utilization)
2. Offer a real-time dashboard for system monitoring
3. Adapt to workload changes automatically
4. Validate performance through testing

## System Components

- **Core Manager**: Implements Banker's Algorithm for safe resource allocation
- **Desktop App**: Tkinter-based UI for resource management
- **Web Dashboard**: Flask/Dash/Plotly for real-time visualization
- **Alerting System**: Monitors resource usage and generates alerts based on thresholds defined in config.json
- **State Manager**: Handles saving and loading of system state

## Key Features

- **Deadlock Prevention**: Uses a modified Banker's Algorithm that allows up to 90% resource utilization
- **Real-time Monitoring**: Desktop and web interfaces for monitoring resource usage
- **Resource Reset**: Automatically resets allocations to 0 on startup for a clean slate
- **State Persistence**: Saves and loads system state between runs
- **Interactive Dashboards**: Real-time charts and visualizations of resource usage
- **Streamlined Alerting System**: Generates alerts when resource usage exceeds thresholds defined in config.json
- **Minimal Console Output**: Only shows essential system information
- **Configuration via JSON**: All settings including alert thresholds configured through config.json

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone : https://github.com/lakshyakumar90/Resguard-Resource-Management-System.git
cd Resguard-Resource-Management-System

# Install dependencies
pip install -r requirements.txt

# Create a configuration file
cp config.json.example config.json

# Run the application
python main.py
```

## Usage

### Basic Usage

```bash
# Run with default settings (resets resources and allocations)
python main.py

# Run without resetting allocations
python main.py --keep-allocations

# Run web dashboard only
python main.py --web-only

# Run desktop application only
python main.py --desktop-only

# Enable alerts (regardless of config.json setting)
python main.py --enable-alerts
```

> **Note:** Debug mode has been disabled by default to reduce console output.

### Desktop Application

1. Start the application using `python main.py`
2. Log in to the desktop application (default: admin/admin)
3. Request resources through the UI by entering process ID and resource amounts
4. Monitor resource usage in real-time
5. Use the Tools menu to reset resources

> **Note:** Alert settings are no longer configurable through the UI and must be set in config.json

### Web Dashboard

1. Access the web dashboard at http://localhost:5000
2. Log in with the same credentials as the desktop app
3. View real-time resource usage charts and system performance metrics
4. See currently allocated resources in a tabular format
5. Monitor top processes by CPU and memory usage

## Configuration

ResGuard is configured exclusively through the `config.json` file:

- **System**: State directory, save intervals, history size
- **Resources**: Available CPU, memory, disk, and network resources
- **Desktop App**: Window title, size, and refresh interval
- **Web Dashboard**: Host, port, and refresh interval
- **Security**: Authentication settings
- **Logging**: Log level, file, size, and backup count
- **Alerting**: Warning and critical thresholds, cooldown periods (only configurable via config.json)

### Sample Alert Configuration

```json
"alerting": {
  "enabled": true,
  "thresholds": {
    "cpu": {
      "warning": 70,
      "critical": 90
    },
    "memory": {
      "warning": 70,
      "critical": 90
    },
    "disk": {
      "warning": 70,
      "critical": 90
    },
    "network": {
      "warning": 70,
      "critical": 90
    }
  },
  "cooldown_period": 300
}
```

## Architecture

ResGuard follows a modular architecture with streamlined components:

```
resguard/
├── core/               # Core logic
│   ├── banker_algorithm.py     # Banker's Algorithm implementation (streamlined)
│   ├── resource_manager.py     # Central resource management
│   ├── thread_manager.py       # Concurrent task handling (simplified)
│   ├── state_manager.py        # State persistence
│   └── alerting_system.py      # Alerting system (config-driven)
├── desktop_app/        # Desktop UI
│   ├── app.py                  # Main application (alert settings GUI removed)
│   ├── dashboard.py            # Resource monitoring UI
│   └── login.py                # Login screen
├── web_dashboard/      # Web UI
│   ├── app.py                  # Flask application
│   ├── dashboard.py            # Dash/Plotly dashboard
│   └── templates/              # HTML templates
├── utils/              # Utilities
│   ├── system_monitor.py       # System monitoring
│   └── config.py               # Configuration management (direct file-based)
├── reports/            # Reporting system
│   └── report_generator.py     # Report generation
└── states/             # State storage
    └── current_state.json      # Current system state
```

### Key Code Optimizations

1. **Banker's Algorithm**: Removed debug print statements for cleaner execution
2. **Resource Manager**: Streamlined console output to essential messages only
3. **Alerting System**: Simplified to use config.json settings only
4. **Thread Manager**: Removed unnecessary functions and optimized execution
5. **Desktop App**: Removed alert settings GUI components and related code
6. **Web Dashboard**: Improved display of process allocations

## Development

### Console Output and Logging

ResGuard has been configured to minimize console output. The only messages that will appear in the console are:

1. "Initializing ResGuard components..." - When the system starts
2. "Resetting resources to default values..." - When resources are reset to defaults
3. Flask server startup messages (when running the web dashboard):
   - "* Serving Flask app ..."
   - "* Debug mode: off"  
   - "WARNING: This is a development server..."
   - "* Running on http://127.0.0.1:5000"
   - "Press CTRL+C to quit"

Critical alerts will still be logged by the alerting system, but they won't be displayed to the console. To access alert history:

1. Use the desktop app's alert history view
2. Check logs if file logging is enabled in config.json

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Recent Updates

### Version 2.0 (June 2025)

- **Simplified Console Output**: Removed unnecessary console logs to improve clarity
- **Fixed Alert Settings**: Alert settings now exclusively configured through config.json
- **Removed Debug Mode**: Reduced excessive diagnostic output
- **Optimized Performance**: Removed redundant code and functions
- **Enhanced Web Dashboard**: Improved visualization of process allocations
- **Streamlined Code Base**: Eliminated unused functions and code paths

## Contributors

- Lakshya Kumar (Team Leader)
- Chitrance Dogra
- Aman Rana
- Anshuman Riar

## Acknowledgments

- The Banker's Algorithm was developed by Edsger Dijkstra
- Thanks to all contributors who have helped shape this project
