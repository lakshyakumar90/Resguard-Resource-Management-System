import json
import os
import time
import threading
from typing import Dict, Any, Optional


class StateManager:

    def __init__(self, state_dir: str = "states"):

        self.state_dir = state_dir
        self.current_state_file = os.path.join(state_dir, "current_state.json")
        self.lock = threading.RLock()
        
        # Create state directory if it doesn't exist
        os.makedirs(state_dir, exist_ok=True)
        
    def save_state(self, state: Dict[str, Any]) -> bool:
       
        with self.lock:
            try:
                # Add timestamp to state
                state["saved_at"] = time.time()
                
                # Save to current state file
                with open(self.current_state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                    
                return True
            except Exception as e:
                # Print statement removed
                return False
                

                
    def load_state(self) -> Dict[str, Any]:
        
        with self.lock:
            try:
                if not os.path.exists(self.current_state_file):
                    return None
                    
                with open(self.current_state_file, 'r') as f:
                    state = json.load(f)
                    
                return state
            except Exception as e:
                # Print statement removed
                return None
