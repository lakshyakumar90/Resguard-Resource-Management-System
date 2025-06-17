import os
import threading
import argparse
import time

from core.resource_manager import ResourceManager
from core.thread_manager import ThreadManager
from core.state_manager import StateManager
from core.alerting_system import AlertingSystem
from utils.system_monitor import SystemMonitor
from utils.config import Config
from desktop_app.app import DesktopApp
from web_dashboard.app import create_app, run_app
from web_dashboard.dashboard import create_dashboard


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ResGuard: Dynamic Resource Management System")

    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--web-only",
        action="store_true",
        help="Run only the web dashboard"
    )

    parser.add_argument(
        "--desktop-only",
        action="store_true",
        help="Run only the desktop application"
    )

    parser.add_argument(
        "--reset-resources",
        action="store_true",
        default=True,  # Always reset resources by default
        help="Reset resources to default values on startup (default: True)"
    )

    parser.add_argument(
        "--no-reset-resources",
        action="store_false",
        dest="reset_resources",
        help="Do not reset resources to default values on startup"
    )

    parser.add_argument(
        "--reset-allocations",
        action="store_true",
        default=True,  # Reset allocations by default
        help="Reset all allocations to 0 on startup (default: True)"
    )

    parser.add_argument(
        "--keep-allocations",
        action="store_false",
        dest="reset_allocations",
        help="Keep previous allocations on startup"
    )

    parser.add_argument(
        "--enable-alerts",
        action="store_true",
        help="Enable resource usage alerts (overrides config)"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    # Load configuration
    config = Config(args.config)

    # Create state directory if it doesn't exist
    state_dir = config.get("system", "state_dir")
    os.makedirs(state_dir, exist_ok=True)

    # Initialize components
    print("Initializing ResGuard components...")

    # Define available resources
    # Always use default values for resources to prevent persistence
    default_resources = {
        "cpu": 100,  # Default CPU units
        "memory": 1000,  # Default memory units (MB)
        "disk": 1000,  # Default disk units (MB)
        "network": 100  # Default network units (Mbps)
    }

    # If not resetting resources, use values from config
    if not args.reset_resources:
        available_resources = {
            "cpu": config.get("resources", "cpu"),
            "memory": config.get("resources", "memory"),
            "disk": config.get("resources", "disk"),
            "network": config.get("resources", "network")
        }
    else:
        print("Resetting resources to default values...")
        available_resources = default_resources.copy()

        # Update config with default values
        for resource, value in default_resources.items():
            config.set("resources", resource, value)
        config.save()

    # Create resource manager
    state_file = os.path.join(state_dir, "current_state.json")
    resource_manager = ResourceManager(
        available_resources,
        state_file,
        reset_on_load=True,
        debug_mode=False,
        reset_allocations=args.reset_allocations
    )

    # Create thread manager
    thread_manager = ThreadManager(resource_manager)

    # Create system monitor
    system_monitor = SystemMonitor(update_interval=1.0)

    # Create state manager
    state_manager = StateManager(state_dir)

    # Try to load previous state
    if os.path.exists(state_file):
        resource_manager.load_state()


    # Create alerting system
    alerting_system = AlertingSystem(resource_manager, system_monitor, config)

    # Use predefined alert settings from config.json
    if config.get("alerting", "enabled") or args.enable_alerts:
        alerting_system.start()



    # Start web dashboard in a separate thread if not desktop-only
    if not args.desktop_only:
        web_thread = threading.Thread(
            target=start_web_dashboard,
            args=(system_monitor, resource_manager, config),
            daemon=True
        )
        web_thread.start()

    # Start desktop application if not web-only
    if not args.web_only:
        start_desktop_app(
            resource_manager,
            thread_manager,
            system_monitor,
            config,
            alerting_system=alerting_system,
            state_manager=state_manager
        )
    else:
        # If web-only, keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Stop alerting system if enabled
            if config.get("alerting", "enabled"):
                alerting_system.stop()

            # Shutdown core components
            resource_manager.shutdown()
            system_monitor.shutdown()


def start_web_dashboard(system_monitor, resource_manager, config):
    """Start the web dashboard."""
    # Create Flask app
    flask_app = create_app(system_monitor, config)
    
    # Store resource_manager in app config
    flask_app.config["RESOURCE_MANAGER"] = resource_manager
    
    # Create Dash app
    dash_app = create_dashboard(flask_app, system_monitor, config)

    # Run Flask app
    host = config.get("web_dashboard", "host")
    port = config.get("web_dashboard", "port")
    
    # Always disable debug mode
    debug = False

    # When running in a thread, we need to pass threaded=True
    run_app(flask_app, host=host, port=port, debug=debug, threaded=True)


def start_desktop_app(resource_manager, thread_manager, system_monitor, config,
                  alerting_system=None, state_manager=None):
    """Start the desktop application."""
    app = DesktopApp(
        resource_manager,
        thread_manager,
        system_monitor,
        config,
        alerting_system=alerting_system,
        state_manager=state_manager
    )
    app.run()


if __name__ == "__main__":
    main()
