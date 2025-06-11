"""
Desktop Application Module

This module provides the main desktop application for the ResGuard system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import time

from core.resource_manager import ResourceManager
from core.thread_manager import ThreadManager
from core.alerting_system import AlertingSystem
from utils.system_monitor import SystemMonitor
from utils.config import Config
from desktop_app.login import LoginScreen
from desktop_app.dashboard import Dashboard




class DesktopApp:
    """
    Main desktop application for the ResGuard system.

    This class provides the main window and coordinates the different
    components of the desktop application.
    """

    def __init__(self, resource_manager: ResourceManager, thread_manager: ThreadManager,
                system_monitor: SystemMonitor, config: Config,
                alerting_system: AlertingSystem = None):
        """
        Initialize the desktop application.

        Args:
            resource_manager: Resource manager instance
            thread_manager: Thread manager instance
            system_monitor: System monitor instance
            config: Configuration object
            alerting_system: Alerting system instance
        """
        self.resource_manager = resource_manager
        self.thread_manager = thread_manager
        self.system_monitor = system_monitor
        self.config = config
        self.alerting_system = alerting_system

        # Create root window
        self.root = tk.Tk()
        self.root.title(config.get("desktop_app", "title"))
        self.root.geometry(f"{config.get('desktop_app', 'width')}x{config.get('desktop_app', 'height')}")

        # Set window icon
        # self.root.iconbitmap("icon.ico")  # Uncomment if you have an icon

        # Configure style
        self._configure_style()

        # Show login screen if authentication is enabled
        if config.get("security", "enable_authentication"):
            self.root.withdraw()  # Hide main window
            LoginScreen(self.root, config, self._on_login_success)
        else:
            self._initialize_ui()

    def _configure_style(self):
        """Configure the application style."""
        style = ttk.Style()

        # Use system theme
        style.theme_use("clam")  # Use a theme that works on most platforms

        # Configure colors
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TButton", padding=5)
        style.configure("TProgressbar", thickness=8)

    def _on_login_success(self, username: str):
        """
        Handle successful login.

        Args:
            username: Username of the logged-in user
        """
        self.username = username
        self.root.deiconify()  # Show main window
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the main UI after login."""
        # Configure root window
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Create menu
        self._create_menu()

        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create dashboard
        self.dashboard = Dashboard(main_frame, self.resource_manager,
                                 self.system_monitor, self.config)
        self.dashboard.pack(fill=tk.BOTH, expand=True)

        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save State", command=self._save_state)
        file_menu.add_command(label="Load State", command=self._load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Web Dashboard", command=self._open_web_dashboard)
        view_menu.add_command(label="Refresh", command=self._refresh)
        menubar.add_cascade(label="View", menu=view_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Generate Report", command=self._generate_report)
        tools_menu.add_separator()
        tools_menu.add_command(label="Reset Resources", command=self._reset_resources)
        tools_menu.add_separator()

        # Add alerting if available
        if self.alerting_system:
            tools_menu.add_command(label="Alert Settings", command=self._open_alert_settings)
            tools_menu.add_command(label="View Alerts", command=self._view_alerts)
            tools_menu.add_separator()

        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _save_state(self):
        """Save the current system state."""
        if self.resource_manager.save_state():
            self.status_var.set("State saved successfully")
            messagebox.showinfo("Success", "System state saved successfully")
        else:
            self.status_var.set("Error saving state")
            messagebox.showerror("Error", "Failed to save system state")

    def _load_state(self):
        """Load system state from file."""
        if self.resource_manager.load_state():
            self.status_var.set("State loaded successfully")
            messagebox.showinfo("Success", "System state loaded successfully")
            self._refresh()
        else:
            self.status_var.set("Error loading state")
            messagebox.showerror("Error", "Failed to load system state")

    def _generate_report(self):
        """Generate resource usage report."""
        try:
            from reports.report_generator import ReportGenerator
            from desktop_app.report_dialog import ReportDialog

            # Show report configuration dialog
            dialog = ReportDialog(self.root, self.config)
            if dialog.result:
                # Generate report with selected options
                report_gen = ReportGenerator(
                    self.resource_manager,
                    self.system_monitor,
                    self.config
                )

                report_path = report_gen.generate_report(
                    time_range=dialog.result.get('time_range', 3600),  # Default 1 hour
                    include_charts=dialog.result.get('include_charts', True),
                    include_tables=dialog.result.get('include_tables', True),
                    report_name=dialog.result.get('report_name', 'resource_usage_report')
                )

                if report_path:
                    self.status_var.set(f"Report generated: {report_path}")
                    if messagebox.askyesno("Report Generated", f"Report saved to:\n{report_path}\n\nWould you like to open it?"):
                        webbrowser.open(f"file://{os.path.abspath(report_path)}")
                else:
                    self.status_var.set("Error generating report")
                    messagebox.showerror("Error", "Failed to generate report")
        except ImportError as e:
            messagebox.showerror("Error", f"Report generation module not available: {e}")
        except Exception as e:
            self.status_var.set("Error generating report")
            messagebox.showerror("Error", f"Error generating report: {e}")

    def open_report_dialog(self):
        """Open the report generation dialog and generate report."""
        from desktop_app.report_dialog import ReportDialog
        from reports.report_generator import ReportGenerator

        dialog = ReportDialog(self.root, self.config)
        if dialog.result is None:
            return  # User cancelled

        # Extract options from dialog result
        options = dialog.result

        # Generate report
        generator = ReportGenerator(self.resource_manager, self.system_monitor, self.config)
        report_path = generator.generate_report(
            time_range=options['time_range'],
            include_charts=options['include_charts'],
            include_tables=options['include_tables'],
            report_name=options['report_name']
        )

        if report_path:
            messagebox.showinfo("Report Generated", f"Report successfully generated at:\n{report_path}")
            # Open the report in the default browser
            import webbrowser
            webbrowser.open(f"file:///{report_path.replace('\\', '/')}")
        else:
            messagebox.showerror("Error", "Failed to generate the report.")

    def _reset_resources(self):
        """Reset resources to initial values."""
        if messagebox.askyesno("Reset Resources", "Are you sure you want to reset all resources to their initial values? This will remove all processes and allocations."):
            if self.resource_manager.reset_resources():
                self.status_var.set("Resources reset successfully")
                messagebox.showinfo("Success", "Resources have been reset to their initial values")
                self._refresh()
            else:
                self.status_var.set("Error resetting resources")
                messagebox.showerror("Error", "Failed to reset resources")

    def _open_web_dashboard(self):
        """Open the web dashboard in a browser."""
        host = self.config.get("web_dashboard", "host")
        port = self.config.get("web_dashboard", "port")
        url = f"http://{host}:{port}"

        try:
            webbrowser.open(url)
            self.status_var.set(f"Web dashboard opened at {url}")
        except Exception as e:
            self.status_var.set("Error opening web dashboard")
            messagebox.showerror("Error", f"Failed to open web dashboard: {e}")

    def _refresh(self):
        """Refresh the dashboard."""
        self.dashboard._refresh_data()
        self.status_var.set("Dashboard refreshed")

    def _show_about(self):
        """Show the about dialog."""
        about_text = """
        ResGuard: Dynamic Resource Management System

        Version: 1.0.0

        A software project to dynamically allocate computing resources
        using the Banker's Algorithm to prevent deadlocks, optimize
        utilization, and provide real-time monitoring.

        2025
        Lakshya Kumar (Team Leader)
        Aman Rana (Team Member)
        Chitrance Dogra (Team Member)
        Anshuman Riar (Team Member)
        """

        messagebox.showinfo("About ResGuard", about_text)

    def _show_help(self):
        """Show the help dialog."""
        help_text = """
        ResGuard Help

        Resource Requests:
        1. Enter a Process ID
        2. Enter resource amounts
        3. Click "Request"

        Resource Releases:
        1. Enter a Process ID
        2. Enter resource amounts
        3. Click "Release"

        Remove Process:
        1. Enter a Process ID
        2. Click "Remove"

        Double-click on a process in the allocation table
        to fill the request form.
        """

        messagebox.showinfo("ResGuard Help", help_text)

    # New feature handlers
    def _view_predictions(self):
        """View resource usage predictions."""
        if not self.predictive_analyzer:
            messagebox.showinfo("Not Available", "Predictive analysis is not enabled.")
            return

        # Get predictions
        predictions = self.predictive_analyzer.get_predictions()

        # Create dialog to display predictions
        dialog = tk.Toplevel(self.root)
        dialog.title("Resource Usage Predictions")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Add content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Resource Usage Predictions", font=("Arial", 14, "bold")).pack(pady=10)

        # Show prediction data
        if not predictions["timestamps"]:
            ttk.Label(frame, text="No prediction data available yet.").pack(pady=20)
        else:
            # Create a simple table
            for resource in ["cpu", "memory", "disk", "network"]:
                ttk.Label(frame, text=f"{resource.upper()} Predictions", font=("Arial", 12)).pack(anchor=tk.W, pady=(10, 5))

                # Show confidence
                confidence = predictions["confidence"][resource]
                ttk.Label(frame, text=f"Confidence: {confidence:.2f}", font=("Arial", 10, "italic")).pack(anchor=tk.W)

                # Show prediction values
                if predictions[resource]:
                    values = [f"{val:.1f}" for val in predictions[resource][:5]]  # Show first 5 predictions
                    ttk.Label(frame, text=f"Next hours: {', '.join(values)}").pack(anchor=tk.W, pady=(0, 10))

        # Close button
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)

    def _open_alert_settings(self):
        """Open alert settings dialog."""
        if not self.alerting_system:
            messagebox.showinfo("Not Available", "Alerting system is not enabled.")
            return

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Alert Settings")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Add content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Alert Settings", font=("Arial", 14, "bold")).pack(pady=10)

        # Enable/disable alerts
        enabled_var = tk.BooleanVar(value=self.config.get("alerting", "enabled"))
        ttk.Checkbutton(frame, text="Enable Alerts", variable=enabled_var).pack(anchor=tk.W, pady=5)

        # Thresholds
        ttk.Label(frame, text="Alert Thresholds:", font=("Arial", 12)).pack(anchor=tk.W, pady=(15, 5))

        # Create threshold inputs for each resource
        threshold_frame = ttk.Frame(frame)
        threshold_frame.pack(fill=tk.X, pady=5)

        thresholds = self.config.get("alerting", "thresholds")
        threshold_vars = {}

        row = 0
        for resource in ["cpu", "memory", "disk", "network"]:
            ttk.Label(threshold_frame, text=f"{resource.upper()}:").grid(row=row, column=0, sticky=tk.W, pady=5)

            # Warning threshold
            ttk.Label(threshold_frame, text="Warning:").grid(row=row, column=1, padx=5)
            warning_var = tk.StringVar(value=str(thresholds[resource]["warning"]))
            ttk.Entry(threshold_frame, textvariable=warning_var, width=5).grid(row=row, column=2)
            ttk.Label(threshold_frame, text="%").grid(row=row, column=3)

            # Critical threshold
            ttk.Label(threshold_frame, text="Critical:").grid(row=row, column=4, padx=5)
            critical_var = tk.StringVar(value=str(thresholds[resource]["critical"]))
            ttk.Entry(threshold_frame, textvariable=critical_var, width=5).grid(row=row, column=5)
            ttk.Label(threshold_frame, text="%").grid(row=row, column=6)

            threshold_vars[resource] = {
                "warning": warning_var,
                "critical": critical_var
            }

            row += 1

        # Notification methods
        ttk.Label(frame, text="Notification Methods:", font=("Arial", 12)).pack(anchor=tk.W, pady=(15, 5))

        notification_methods = self.config.get("alerting", "notification_methods")
        method_vars = {}

        for method in ["console", "email", "webhook"]:
            var = tk.BooleanVar(value=notification_methods.get(method, False))
            ttk.Checkbutton(frame, text=method.capitalize(), variable=var).pack(anchor=tk.W)
            method_vars[method] = var

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=15)

        ttk.Button(button_frame, text="Save", command=lambda: self._save_alert_settings(
            enabled_var.get(), threshold_vars, method_vars, dialog
        )).pack(side=tk.RIGHT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _save_alert_settings(self, enabled, threshold_vars, method_vars, dialog):
        """Save alert settings."""
        try:
            # Update configuration
            self.config.set("alerting", "enabled", enabled)

            # Update thresholds
            thresholds = self.config.get("alerting", "thresholds")
            for resource, vars in threshold_vars.items():
                warning = int(vars["warning"].get())
                critical = int(vars["critical"].get())

                if warning >= critical:
                    messagebox.showerror("Invalid Input", f"Warning threshold must be less than critical threshold for {resource}.")
                    return

                if warning < 0 or warning > 100 or critical < 0 or critical > 100:
                    messagebox.showerror("Invalid Input", "Thresholds must be between 0 and 100.")
                    return

                thresholds[resource]["warning"] = warning
                thresholds[resource]["critical"] = critical

            # Update notification methods
            notification_methods = self.config.get("alerting", "notification_methods")
            for method, var in method_vars.items():
                notification_methods[method] = var.get()

            # Save configuration
            self.config.save()

            # Close dialog
            dialog.destroy()

            # Show success message
            messagebox.showinfo("Success", "Alert settings saved successfully.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Thresholds must be numeric values.")

    def _view_alerts(self):
        """View active alerts."""
        if not self.alerting_system:
            messagebox.showinfo("Not Available", "Alerting system is not enabled.")
            return

        # Get active alerts
        active_alerts = self.alerting_system.get_active_alerts()
        alert_history = self.alerting_system.get_alert_history()

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Alerts")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Add content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Active alerts tab
        active_tab = ttk.Frame(notebook, padding=10)
        notebook.add(active_tab, text="Active Alerts")

        if not active_alerts:
            ttk.Label(active_tab, text="No active alerts.").pack(pady=20)
        else:
            # Create table
            columns = ("resource", "severity", "value", "threshold", "time")
            tree = ttk.Treeview(active_tab, columns=columns, show="headings")

            # Define headings
            tree.heading("resource", text="Resource")
            tree.heading("severity", text="Severity")
            tree.heading("value", text="Current Value")
            tree.heading("threshold", text="Threshold")
            tree.heading("time", text="Time")

            # Define columns
            tree.column("resource", width=100)
            tree.column("severity", width=100)
            tree.column("value", width=100)
            tree.column("threshold", width=100)
            tree.column("time", width=150)

            # Add data
            for alert_id, alert in active_alerts.items():
                tree.insert("", "end", values=(
                    alert["resource"].upper(),
                    alert["severity"].upper(),
                    f"{alert['current_value']:.1f}%",
                    f"{alert['threshold']}%",
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert["last_triggered"]))
                ))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(active_tab, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)

        # History tab
        history_tab = ttk.Frame(notebook, padding=10)
        notebook.add(history_tab, text="Alert History")

        if not alert_history:
            ttk.Label(history_tab, text="No alert history.").pack(pady=20)
        else:
            # Create table
            columns = ("resource", "severity", "value", "threshold", "time", "status")
            tree = ttk.Treeview(history_tab, columns=columns, show="headings")

            # Define headings
            tree.heading("resource", text="Resource")
            tree.heading("severity", text="Severity")
            tree.heading("value", text="Value")
            tree.heading("threshold", text="Threshold")
            tree.heading("time", text="Time")
            tree.heading("status", text="Status")

            # Define columns
            tree.column("resource", width=80)
            tree.column("severity", width=80)
            tree.column("value", width=80)
            tree.column("threshold", width=80)
            tree.column("time", width=150)
            tree.column("status", width=80)

            # Add data (most recent first)
            for alert in reversed(alert_history):
                tree.insert("", "end", values=(
                    alert["resource"].upper(),
                    alert["severity"].upper(),
                    f"{alert['current_value']:.1f}%",
                    f"{alert['threshold']}%",
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert["last_triggered"])),
                    "Active" if alert.get("active", False) else "Resolved"
                ))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(history_tab, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)

        # Close button
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)







    def _open_alert_settings(self):
        """Open alert settings."""
        if not self.alerting_system:
            messagebox.showinfo("Not Available", "Alerting system is not enabled.")
            return

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Alert Settings")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Add content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Alert Settings", font=("Arial", 14, "bold")).pack(pady=10)

        # Enable/disable alerts
        enabled_var = tk.BooleanVar(value=self.config.get("alerting", "enabled"))
        ttk.Checkbutton(frame, text="Enable Alerts", variable=enabled_var).pack(anchor=tk.W, pady=5)

        # Thresholds
        ttk.Label(frame, text="Alert Thresholds:", font=("Arial", 12)).pack(anchor=tk.W, pady=(15, 5))

        # Create threshold inputs for each resource
        threshold_frame = ttk.Frame(frame)
        threshold_frame.pack(fill=tk.X, pady=5)

        # Get current thresholds
        thresholds = self.config.get("alerting", "thresholds")
        if not thresholds:
            thresholds = {
                "cpu": {"warning": 70, "critical": 90},
                "memory": {"warning": 70, "critical": 90},
                "disk": {"warning": 70, "critical": 90},
                "network": {"warning": 70, "critical": 90}
            }

        # Create variables for thresholds
        threshold_vars = {}
        row = 0
        for resource in ["cpu", "memory", "disk", "network"]:
            ttk.Label(threshold_frame, text=f"{resource.capitalize()}:").grid(row=row, column=0, sticky=tk.W, pady=5)

            # Warning threshold
            ttk.Label(threshold_frame, text="Warning:").grid(row=row, column=1, padx=5)
            warning_var = tk.StringVar(value=str(thresholds.get(resource, {}).get("warning", 70)))
            ttk.Entry(threshold_frame, textvariable=warning_var, width=5).grid(row=row, column=2)
            ttk.Label(threshold_frame, text="%").grid(row=row, column=3)

            # Critical threshold
            ttk.Label(threshold_frame, text="Critical:").grid(row=row, column=4, padx=5)
            critical_var = tk.StringVar(value=str(thresholds.get(resource, {}).get("critical", 90)))
            ttk.Entry(threshold_frame, textvariable=critical_var, width=5).grid(row=row, column=5)
            ttk.Label(threshold_frame, text="%").grid(row=row, column=6)

            threshold_vars[resource] = {"warning": warning_var, "critical": critical_var}
            row += 1

        # Cooldown period
        ttk.Label(frame, text="Cooldown Period:", font=("Arial", 12)).pack(anchor=tk.W, pady=(15, 5))
        cooldown_frame = ttk.Frame(frame)
        cooldown_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cooldown_frame, text="Time between alerts:").grid(row=0, column=0, sticky=tk.W)
        cooldown_var = tk.StringVar(value=str(self.config.get("alerting", "cooldown_period") or 300))
        ttk.Entry(cooldown_frame, textvariable=cooldown_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(cooldown_frame, text="seconds").grid(row=0, column=2, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=15)

        ttk.Button(button_frame, text="Save", command=lambda: self._save_alert_settings(
            enabled_var.get(), threshold_vars, cooldown_var.get(), dialog
        )).pack(side=tk.RIGHT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _save_alert_settings(self, enabled, threshold_vars, cooldown, dialog):
        """Save alert settings."""
        try:
            # Validate inputs
            cooldown = int(cooldown)
            if cooldown <= 0:
                messagebox.showerror("Invalid Input", "Cooldown period must be a positive number.")
                return

            # Validate and collect thresholds
            thresholds = {}
            for resource, vars in threshold_vars.items():
                warning = int(vars["warning"].get())
                critical = int(vars["critical"].get())

                if warning < 0 or warning > 100 or critical < 0 or critical > 100:
                    messagebox.showerror("Invalid Input", "Thresholds must be between 0 and 100.")
                    return

                if warning >= critical:
                    messagebox.showerror("Invalid Input", f"Warning threshold must be less than critical threshold for {resource}.")
                    return

                thresholds[resource] = {"warning": warning, "critical": critical}

            # Update configuration
            self.config.set("alerting", "enabled", enabled)
            self.config.set("alerting", "thresholds", thresholds)
            self.config.set("alerting", "cooldown_period", cooldown)

            # Save configuration
            self.config.save()

            # Close dialog
            dialog.destroy()

            # Show success message
            messagebox.showinfo("Success", "Alert settings saved successfully.")

            # Restart alerting system if it's running
            if self.alerting_system:
                self.alerting_system.stop()
                if enabled:
                    self.alerting_system.start()

        except ValueError:
            messagebox.showerror("Invalid Input", "All values must be numeric.")

    def _view_alerts(self):
        """View alert history."""
        if not self.alerting_system:
            messagebox.showinfo("Not Available", "Alerting system is not enabled.")
            return

        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Alert History")
        dialog.geometry("800x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Add content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Alert History", font=("Arial", 14, "bold")).pack(pady=10)

        # Create treeview for alerts
        columns = ("timestamp", "resource", "severity", "value", "threshold", "message")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        # Define column headings
        tree.heading("timestamp", text="Time")
        tree.heading("resource", text="Resource")
        tree.heading("severity", text="Severity")
        tree.heading("value", text="Value")
        tree.heading("threshold", text="Threshold")
        tree.heading("message", text="Message")

        # Define column widths
        tree.column("timestamp", width=150)
        tree.column("resource", width=80)
        tree.column("severity", width=80)
        tree.column("value", width=60)
        tree.column("threshold", width=80)
        tree.column("message", width=250)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Get alert history
        alerts = self.alerting_system.get_alert_history()

        # Add alerts to tree
        for alert in reversed(alerts):  # Show newest first
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert["timestamp"]))
            tree.insert("", "end", values=(
                timestamp,
                alert["resource"],
                alert["severity"].upper(),
                f"{alert['current_value']:.1f}%",
                f"{alert['threshold']}%",
                alert["message"]
            ))

        # Add button to close dialog
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)





    def _on_close(self):
        """Handle application close."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Save state before exit
            self.resource_manager.save_state()

            # Shutdown components
            self.system_monitor.shutdown()
            self.resource_manager.shutdown()



            # Stop alerting system if available
            if self.alerting_system:
                self.alerting_system.stop()

            # Close window
            self.root.destroy()

    def run(self):
        """Run the application."""
        self.root.mainloop()
