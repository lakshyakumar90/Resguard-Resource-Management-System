"""
Report Dialog Module

This module provides a dialog for configuring report generation options.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Any


class ReportDialog:
    """
    Dialog for configuring report generation options.
    """
    
    def __init__(self, parent: tk.Tk, config: Any):
        """
        Initialize the report dialog.
        
        Args:
            parent: Parent window
            config: Configuration object
        """
        self.parent = parent
        self.config = config
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Generate Resource Usage Report")
        # Set a fixed size for the dialog
        self.dialog.geometry("900x900")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the screen
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Create widgets
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Create and arrange dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Report Generation Options", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Report name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Report Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value="resource_usage_report")
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=30)
        name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Time range selection
        time_frame = ttk.LabelFrame(main_frame, text="Time Range", padding=10)
        time_frame.pack(fill=tk.X, pady=10)
        
        self.time_var = tk.StringVar(value="1_hour")
        
        time_options = [
            ("Last 30 minutes", "30_min", 1800),
            ("Last 1 hour", "1_hour", 3600),
            ("Last 2 hours", "2_hours", 7200),
            ("Last 6 hours", "6_hours", 21600),
            ("Last 12 hours", "12_hours", 43200),
            ("Last 24 hours", "24_hours", 86400)
        ]
        
        self.time_values = {}
        for text, value, seconds in time_options:
            rb = ttk.Radiobutton(time_frame, text=text, variable=self.time_var, value=value)
            rb.pack(anchor=tk.W, pady=2)
            self.time_values[value] = seconds
        
        # Content options
        content_frame = ttk.LabelFrame(main_frame, text="Report Content", padding=10)
        content_frame.pack(fill=tk.X, pady=10)
        
        self.include_charts_var = tk.BooleanVar(value=True)
        charts_cb = ttk.Checkbutton(content_frame, text="Include Charts and Graphs", 
                                   variable=self.include_charts_var)
        charts_cb.pack(anchor=tk.W, pady=2)
        
        self.include_tables_var = tk.BooleanVar(value=True)
        tables_cb = ttk.Checkbutton(content_frame, text="Include Data Tables", 
                                   variable=self.include_tables_var)
        tables_cb.pack(anchor=tk.W, pady=2)
        
        self.include_summary_var = tk.BooleanVar(value=True)
        summary_cb = ttk.Checkbutton(content_frame, text="Include Summary Statistics", 
                                    variable=self.include_summary_var)
        summary_cb.pack(anchor=tk.W, pady=2)
        
        self.include_history_var = tk.BooleanVar(value=True)
        history_cb = ttk.Checkbutton(content_frame, text="Include Request History", 
                                    variable=self.include_history_var)
        history_cb.pack(anchor=tk.W, pady=2)
        
        # Format options
        format_frame = ttk.LabelFrame(main_frame, text="Output Format", padding=10)
        format_frame.pack(fill=tk.X, pady=10)
        
        self.format_var = tk.StringVar(value="html")
        
        html_rb = ttk.Radiobutton(format_frame, text="HTML Report (Recommended)", 
                                 variable=self.format_var, value="html")
        html_rb.pack(anchor=tk.W, pady=2)
        
        # Note about HTML format
        note_label = ttk.Label(format_frame, text="HTML reports include interactive charts and can be viewed in any web browser.", 
                              font=("Arial", 9), foreground="gray")
        note_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Generate Report", command=self._on_generate).pack(side=tk.RIGHT)
        
        # Add some help text
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(10, 0))
        
        help_text = ("The report will include current system status, resource allocation information, "
                    "and historical data for the selected time period. Charts show resource usage trends "
                    "over time, while tables provide detailed process and allocation information.")
        
        help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 9), 
                              foreground="gray", wraplength=450, justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
    
    def _on_generate(self):
        """Handle generate button click."""
        # Validate inputs
        report_name = self.name_var.get().strip()
        if not report_name:
            messagebox.showerror("Error", "Please enter a report name.")
            return
        
        # Check if at least one content option is selected
        if not any([
            self.include_charts_var.get(),
            self.include_tables_var.get(),
            self.include_summary_var.get(),
            self.include_history_var.get()
        ]):
            messagebox.showerror("Error", "Please select at least one content option.")
            return
        
        # Prepare result
        time_range_seconds = self.time_values.get(self.time_var.get(), 3600)
        
        self.result = {
            'report_name': report_name,
            'time_range': time_range_seconds,
            'include_charts': self.include_charts_var.get(),
            'include_tables': self.include_tables_var.get(),
            'include_summary': self.include_summary_var.get(),
            'include_history': self.include_history_var.get(),
            'format': self.format_var.get()
        }
        
        # Close dialog
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
