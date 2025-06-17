import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
from typing import Callable

from utils.system_monitor import SystemMonitor
from utils.config import Config

def create_app(system_monitor: SystemMonitor, config: Config) -> Flask:

    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Store components in app config
    app.config["SYSTEM_MONITOR"] = system_monitor
    app.config["APP_CONFIG"] = config

    # Authentication decorator
    def login_required(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if config.get("security", "enable_authentication") and "username" not in session:
                return redirect(url_for("login", next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    # Routes
    @app.route("/")
    @login_required
    def index():
        """Render the main dashboard page."""
        return render_template("index.html")



    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle login requests."""
        if not config.get("security", "enable_authentication"):
            return redirect(url_for("index"))

        error = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if (username == config.get("security", "default_username") and
                password == config.get("security", "default_password")):
                session["username"] = username
                return redirect(request.args.get("next") or url_for("index"))
            else:
                error = "Invalid username or password"

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        """Handle logout requests."""
        session.pop("username", None)
        return redirect(url_for("login"))

    @app.route("/api/system")
    @login_required
    def api_system():
        """API endpoint for system metrics."""
        return jsonify(system_monitor.get_metrics())

    @app.route("/api/system/history")
    @login_required
    def api_system_history():
        """API endpoint for system metrics history."""
        return jsonify(system_monitor.get_history())

    @app.route("/api/system/processes")
    @login_required
    def api_processes():
        """API endpoint for process information."""
        sort_by = request.args.get("sort", "cpu")
        return jsonify(system_monitor.get_processes(sort_by=sort_by))

    @app.route("/api/system/allocations")
    @login_required
    def api_allocations():
        """API endpoint for resource allocation information."""
        resource_manager = app.config.get("RESOURCE_MANAGER", None)
        if resource_manager:
            return jsonify(resource_manager.get_system_state())
        else:
            return jsonify({"error": "Resource manager not available"})


    return app


def run_app(app: Flask, host: str = "127.0.0.1", port: int = 5000,
           debug: bool = False, threaded: bool = True) -> None:

    # Always disable debug mode to avoid excessive logging
    debug = False

    app.run(host=host, port=port, debug=debug, use_reloader=False)
