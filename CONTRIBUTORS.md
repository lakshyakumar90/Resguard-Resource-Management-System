# ResGuard Project Contributors

This document provides a detailed breakdown of the contributions made by each team member to the ResGuard Resource Management System project.

## Core Team Members

### Lakshya Kumar (Team Leader)

**Areas of Responsibility:**
* Core System Architecture
* Resource Allocation Logic
* System Utilities
* Report Generation

**Files and Components Developed:**
1. **Core Module:**
   * `banker_algorithm.py` - Implementation of the modified Banker's Algorithm for deadlock prevention
   * `resource_manager.py` - Central resource management component coordinating all resource requests
   * `thread_manager.py` - Thread management for concurrent processing of resource requests
   * `state_manager.py` - System state persistence and recovery
   * `alerting_system.py` - Resource usage monitoring and alert generation

2. **Utils Module:**
   * `config.py` - Configuration management system for application settings
   * `system_monitor.py` - System resource monitoring and metrics collection

3. **Reports Module:**
   * `report_generator.py` - Generation of system reports for resource usage analysis
   * Report template design and implementation
   
4. **System Integration:**
   * `main.py` - Main application entry point and component orchestration
   * System startup and shutdown sequences

5. **Project Management:**
   * Software architecture design
   * Technical documentation
   * Code review and quality assurance

### Chitrance Dogra

**Areas of Responsibility:**
* Desktop Application GUI
* User Interface Design
* Interactive Data Visualization

**Files and Components Developed:**
1. **Desktop Application Module:**
   * `app.py` - Main desktop application with Tkinter framework
   * `dashboard.py` - Resource monitoring and visualization dashboard
   * `login.py` - User authentication interface
   * `report_dialog.py` - Report generation interface

2. **UI Related Features:**
   * User interface layout and navigation
   * Real-time resource usage graphs and charts
   * Process management interfaces
   * Resource allocation request forms
   * Settings interfaces

3. **User Experience:**
   * UI testing and refinement
   * User interaction flows
   * Error handling and user feedback

### Anshuman Riar

**Areas of Responsibility:**
* Web Server Implementation
* API Development
* Authentication System

**Files and Components Developed:**
1. **Web Application Infrastructure:**
   * `web_dashboard/app.py` - Flask server implementation and route configuration
   * RESTful API endpoints for resource data
   * Authentication and session management
   * Server configuration and performance optimization

2. **Backend Integration:**
   * Data transformation for web presentation
   * API security measures
   * Backend error handling
   * Server-side validation

3. **Web Features:**
   * Login system implementation
   * HTTP request processing
   * Server deployment configurations

### Aman Rana

**Areas of Responsibility:**
* Web Dashboard Interface
* Data Visualization
* Frontend Development

**Files and Components Developed:**
1. **Web Dashboard Module:**
   * `web_dashboard/dashboard.py` - Dash/Plotly dashboard implementation
   * `web_dashboard/templates/` - HTML templates for web interface
   * Interactive charts and graphs for resource monitoring
   * Frontend styling and responsive design

2. **Data Visualization:**
   * Real-time resource usage charts
   * Process allocation tables
   * System metrics display
   * Historical data visualization

3. **User Interface Elements:**
   * Dashboard layout and components
   * Interactive controls and filters
   * Client-side data processing
   * Cross-browser compatibility

## Collaborative Work

All team members contributed to the following project aspects:

* **Requirements Analysis:** Identifying and prioritizing system features
* **Testing:** Unit testing, integration testing, and system testing
* **Bug Fixing:** Identifying and resolving issues across the codebase
* **Documentation:** Code comments, README, and technical documentation
* **Project Presentations:** Preparing and delivering project demonstrations

## Recent System Optimization (June 2025)

The team collectively worked on streamlining the system by:

1. Removing unnecessary console output and debug code
2. Simplifying the alerting system to use config-based settings
3. Optimizing code paths and removing redundant functions
4. Improving web dashboard visualizations
5. Enhancing documentation for better system understanding

---

*This document was last updated on June 17, 2025.*
