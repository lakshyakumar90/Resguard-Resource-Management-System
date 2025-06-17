import json
import os
import copy
from typing import Dict, Any, Optional, List, Tuple, Union


class Config:
    def __init__(self, config_file: str = "config.json"):
      
        self.config_file = config_file
        self.config = self._load_default_config()

        # Load configuration from file if it exists
        if os.path.exists(config_file):
            self.load()

    def _load_default_config(self) -> Dict[str, Any]:
        
        # Define the default configuration
        self.default_config = {
            "system": {
                "state_dir": "states",
                "state_save_interval": 60,  # seconds
                "max_history_size": 1000
            },
            "resources": {
                "cpu": 100,  # percentage units
                "memory": 1000,  # MB
                "disk": 1000,  # MB
                "network": 100  # Mbps
            },
            "desktop_app": {
                "title": "ResGuard Resource Manager",
                "width": 800,
                "height": 600,
                "refresh_interval": 1.0  # seconds
            },
            "web_dashboard": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": False,
                "refresh_interval": 1.0  # seconds
            },
            "security": {
                "enable_authentication": True,
                "default_username": "admin",
                "default_password": "admin"
            },
            "logging": {
                "level": "INFO",
                "file": "resguard.log",
                "max_size": 10485760,  # 10 MB
                "backup_count": 5
            },



            "alerting": {
                "enabled": True,
                "thresholds": {
                    "cpu": {"warning": 70, "critical": 90},
                    "memory": {"warning": 70, "critical": 90},
                    "disk": {"warning": 70, "critical": 90},
                    "network": {"warning": 70, "critical": 90}
                },
                "cooldown_period": 300  # seconds
            },


        }

        # Return a deep copy of the default configuration
        return copy.deepcopy(self.default_config)

    def load(self) -> bool:
       
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)

            # Update configuration with loaded values
            self._update_dict(self.config, loaded_config)
            return True
        except Exception:
            return False

    def save(self) -> bool:
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

            return True
        except Exception:
            return False

    def get(self, section: str, key: Optional[str] = None) -> Any:
        
        if section not in self.config:
            return None

        if key is None:
            return self.config[section]

        return self.config[section].get(key)

    def set(self, section: str, key: str, value: Any) -> bool:
       
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        return True

    def get_all(self) -> Dict[str, Any]:
        
        return self.config.copy()

    def _update_dict(self, target: Dict, source: Dict) -> None:
        
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value

    def reset_to_defaults(self) -> bool:
        
        try:
            self.config = copy.deepcopy(self.default_config)
            return True
        except Exception:
            return False

    def reset_section(self, section: str) -> bool:
        
        if section not in self.default_config:
            return False

        try:
            self.config[section] = copy.deepcopy(self.default_config[section])
            return True
        except Exception:
            return False

    def validate(self) -> List[str]:
        
        errors = []

        # Validate system section
        system = self.config.get("system", {})
        if not isinstance(system.get("state_save_interval"), (int, float)) or system.get("state_save_interval") <= 0:
            errors.append("System state_save_interval must be a positive number")
        if not isinstance(system.get("max_history_size"), int) or system.get("max_history_size") <= 0:
            errors.append("System max_history_size must be a positive integer")

        # Validate resources section
        resources = self.config.get("resources", {})
        for resource in ["cpu", "memory", "disk", "network"]:
            if not isinstance(resources.get(resource), (int, float)) or resources.get(resource) <= 0:
                errors.append(f"Resource {resource} must be a positive number")

        # Validate desktop_app section
        desktop = self.config.get("desktop_app", {})
        if not isinstance(desktop.get("width"), int) or desktop.get("width") <= 0:
            errors.append("Desktop app width must be a positive integer")
        if not isinstance(desktop.get("height"), int) or desktop.get("height") <= 0:
            errors.append("Desktop app height must be a positive integer")
        if not isinstance(desktop.get("refresh_interval"), (int, float)) or desktop.get("refresh_interval") <= 0:
            errors.append("Desktop app refresh_interval must be a positive number")

        # Validate web_dashboard section
        web = self.config.get("web_dashboard", {})
        if not isinstance(web.get("port"), int) or web.get("port") <= 0 or web.get("port") > 65535:
            errors.append("Web dashboard port must be a valid port number (1-65535)")
        if not isinstance(web.get("refresh_interval"), (int, float)) or web.get("refresh_interval") <= 0:
            errors.append("Web dashboard refresh_interval must be a positive number")

        # Validate security section
        security = self.config.get("security", {})
        if not isinstance(security.get("enable_authentication"), bool):
            errors.append("Security enable_authentication must be a boolean")
        if security.get("enable_authentication") and not security.get("default_username"):
            errors.append("Security default_username is required when authentication is enabled")
        if security.get("enable_authentication") and not security.get("default_password"):
            errors.append("Security default_password is required when authentication is enabled")

        # Validate logging section
        logging = self.config.get("logging", {})
        if logging.get("level") not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Logging level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        if not isinstance(logging.get("max_size"), int) or logging.get("max_size") <= 0:
            errors.append("Logging max_size must be a positive integer")
        if not isinstance(logging.get("backup_count"), int) or logging.get("backup_count") < 0:
            errors.append("Logging backup_count must be a non-negative integer")

        return errors

    def get_settings_metadata(self) -> Dict[str, List[Dict[str, Any]]]:
        
        return {
            "system": [
                {"name": "state_dir", "type": "string", "label": "State Directory", "description": "Directory to store state files"},
                {"name": "state_save_interval", "type": "number", "label": "State Save Interval", "description": "Time between state saves in seconds", "min": 1},
                {"name": "max_history_size", "type": "number", "label": "Max History Size", "description": "Maximum number of history entries to keep", "min": 10}
            ],
            "resources": [
                {"name": "cpu", "type": "number", "label": "CPU Units", "description": "Total CPU units available", "min": 1},
                {"name": "memory", "type": "number", "label": "Memory Units", "description": "Total memory units available (MB)", "min": 1},
                {"name": "disk", "type": "number", "label": "Disk Units", "description": "Total disk units available (MB)", "min": 1},
                {"name": "network", "type": "number", "label": "Network Units", "description": "Total network bandwidth available (Mbps)", "min": 1}
            ],
            "desktop_app": [
                {"name": "title", "type": "string", "label": "Window Title", "description": "Title of the desktop application window"},
                {"name": "width", "type": "number", "label": "Window Width", "description": "Width of the desktop application window", "min": 400},
                {"name": "height", "type": "number", "label": "Window Height", "description": "Height of the desktop application window", "min": 300},
                {"name": "refresh_interval", "type": "number", "label": "Refresh Interval", "description": "Time between UI refreshes in seconds", "min": 0.1, "step": 0.1}
            ],
            "web_dashboard": [
                {"name": "host", "type": "string", "label": "Host", "description": "Host to bind the web server to"},
                {"name": "port", "type": "number", "label": "Port", "description": "Port to bind the web server to", "min": 1, "max": 65535},
                {"name": "debug", "type": "boolean", "label": "Debug Mode", "description": "Enable debug mode for the web server"},
                {"name": "refresh_interval", "type": "number", "label": "Refresh Interval", "description": "Time between dashboard refreshes in seconds", "min": 0.1, "step": 0.1}
            ],
            "security": [
                {"name": "enable_authentication", "type": "boolean", "label": "Enable Authentication", "description": "Require login for the application"},
                {"name": "default_username", "type": "string", "label": "Default Username", "description": "Default administrator username"},
                {"name": "default_password", "type": "password", "label": "Default Password", "description": "Default administrator password"}
            ],
            "logging": [
                {"name": "level", "type": "select", "label": "Log Level", "description": "Logging verbosity level",
                 "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                {"name": "file", "type": "string", "label": "Log File", "description": "Path to the log file"},
                {"name": "max_size", "type": "number", "label": "Max Log Size", "description": "Maximum size of log file in bytes", "min": 1024},
                {"name": "backup_count", "type": "number", "label": "Backup Count", "description": "Number of backup log files to keep", "min": 0}
            ],

            "alerting": [
                {"name": "enabled", "type": "boolean", "label": "Enable Alerting", "description": "Enable resource usage alerts"},
                {"name": "cooldown_period", "type": "number", "label": "Cooldown Period", "description": "Time between alerts in seconds", "min": 1}
            ],

        }
