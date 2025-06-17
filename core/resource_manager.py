import json
import time
import threading
from typing import Dict, Any

from core.banker_algorithm import BankerAlgorithm


class ResourceManager:
    def __init__(self, available_resources: Dict[str, int], state_file: str = "system_state.json", reset_on_load: bool = False, debug_mode: bool = True, reset_allocations: bool = False):
        
        self.initial_resources = available_resources.copy()  # Store initial resources
        self.debug_mode = debug_mode  # Whether to print debug information
        self.banker = BankerAlgorithm(available_resources, debug_mode=debug_mode)
        self.state_file = state_file
        self.lock = threading.RLock()
        self.process_info = {}  # Additional process information
        self.request_history = []  # History of resource requests
        self.last_saved = 0  # Timestamp of last state save
        self.save_interval = 60  # Save state every 60 seconds
        self.reset_on_load = reset_on_load  # Whether to reset resources on load
        self.reset_allocations = reset_allocations  # Whether to reset allocations on startup

        # Debug prints removed

        # Start background thread for periodic state saving
        self.running = True
        self.save_thread = threading.Thread(target=self._periodic_save, daemon=True)
        self.save_thread.start()

    def register_process(self, process_id: str, max_resources: Dict[str, int],
                         metadata: Dict[str, Any] = None) -> bool:
        
        with self.lock:
            if self.banker.register_process(process_id, max_resources):
                self.process_info[process_id] = {
                    "registered_at": time.time(),
                    "metadata": metadata or {},
                    "status": "registered"
                }
                self._log_event("register", process_id, max_resources)
                return True
            return False

    def request_resources(self, process_id: str, request: Dict[str, int]) -> bool:
        
        with self.lock:
            result = self.banker.request_resources(process_id, request)
            if result:
                self.process_info[process_id]["status"] = "running"
                self._log_event("request", process_id, request, success=True)
            else:
                self._log_event("request", process_id, request, success=False)
            return result

    def release_resources(self, process_id: str, release: Dict[str, int]) -> bool:
        
        with self.lock:
            result = self.banker.release_resources(process_id, release)
            if result:
                self._log_event("release", process_id, release)
            return result

    def remove_process(self, process_id: str) -> bool:
        
        with self.lock:
            result = self.banker.remove_process(process_id)
            if result:
                self.process_info.pop(process_id, None)
                self._log_event("remove", process_id, {})
            return result

    def get_system_state(self) -> Dict:
        
        with self.lock:
            state = self.banker.get_state()
            state["process_info"] = self.process_info
            state["request_history"] = self.request_history[-100:]  # Last 100 requests
            return state

    def save_state(self) -> bool:
        
        try:
            with self.lock:
                state = self.get_system_state()
                with open(self.state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                self.last_saved = time.time()
                return True
        except Exception as e:
            # Print statement removed
            return False

    def load_state(self) -> bool:
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            with self.lock:
                # Determine which resources to use
                if self.reset_on_load:
                    # Use initial resources if resetting
                    available_resources = self.initial_resources.copy()
                else:
                    # Use saved resources
                    available_resources = state["available"]

                # Recreate banker with appropriate resources
                self.banker = BankerAlgorithm(available_resources, debug_mode=self.debug_mode)

                # Restore processes
                for pid, max_claim in state["max_claim"].items():
                    self.banker.register_process(pid, max_claim)

                # Restore allocations only if not resetting them
                if not self.reset_allocations:
                    for pid, allocation in state["allocation"].items():
                        for resource, amount in allocation.items():
                            if amount > 0:
                                self.banker.request_resources(pid, {resource: amount})

                # Restore process info
                self.process_info = state.get("process_info", {})
                self.request_history = state.get("request_history", [])

                return True
        except Exception as e:
            # Print statement removed
            return False

    def set_system_state(self, state: dict) -> bool:
        
        try:
            with self.lock:
                # Determine which resources to use
                if self.reset_on_load:
                    available_resources = self.initial_resources.copy()
                else:
                    available_resources = state["available"]

                # Recreate banker with appropriate resources
                self.banker = BankerAlgorithm(available_resources, debug_mode=self.debug_mode)

                # Restore processes
                for pid, max_claim in state.get("max_claim", {}).items():
                    self.banker.register_process(pid, max_claim)

                # Restore allocations only if not resetting them
                if not self.reset_allocations:
                    for pid, allocation in state.get("allocation", {}).items():
                        for resource, amount in allocation.items():
                            if amount > 0:
                                self.banker.request_resources(pid, {resource: amount})

                # Restore process info
                self.process_info = state.get("process_info", {})
                self.request_history = state.get("request_history", [])

                return True
        except Exception as e:
            # Print statement removed
            return False

    def _log_event(self, event_type: str, process_id: str, resources: Dict[str, int],
                  success: bool = True) -> None:
        
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "process_id": process_id,
            "resources": resources,
            "success": success
        }
        self.request_history.append(event)

        # If we have too many events, trim the history
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def _periodic_save(self) -> None:
        """Background thread for periodic state saving."""
        while self.running:
            time.sleep(5)  # Check every 5 seconds

            current_time = time.time()
            if current_time - self.last_saved >= self.save_interval:
                self.save_state()

    def shutdown(self) -> None:
        """Shutdown the resource manager and save final state."""
        self.running = False
        if self.save_thread.is_alive():
            self.save_thread.join(timeout=2)
        self.save_state()

    def reset_resources(self) -> bool:
        
        with self.lock:
            try:
                # Create a new banker with initial resources
                self.banker = BankerAlgorithm(self.initial_resources.copy(), debug_mode=self.debug_mode)

                # Clear all processes and allocations
                old_process_count = len(self.process_info)
                self.process_info = {}
                self.request_history = []

                # Only keep essential print
                print("Resetting resources to default values...")

                return True
            except Exception as e:
                # Print statement removed
                return False
