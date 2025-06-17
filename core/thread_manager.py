import threading
import time
import uuid
from typing import Dict, List, Callable, Any, Optional, Tuple

from core.resource_manager import ResourceManager


class ThreadManager:
  
    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize the thread manager.
        
        Args:
            resource_manager: The central resource manager
        """
        self.resource_manager = resource_manager
        self.tasks = {}  # Dictionary of running tasks
        self.lock = threading.RLock()
        self.task_results = {}  # Store results of completed tasks
        
    def submit_task(self, task_func: Callable, max_resources: Dict[str, int], 
                   args: tuple = (), kwargs: Dict[str, Any] = None) -> str:
        
        task_id = f"task-{uuid.uuid4()}"
        kwargs = kwargs or {}
        
        with self.lock:
            # Register the task with the resource manager
            if not self.resource_manager.register_process(task_id, max_resources, 
                                                         {"type": "task", "function": task_func.__name__}):
                return None
                
            # Create task entry
            self.tasks[task_id] = {
                "id": task_id,
                "function": task_func,
                "args": args,
                "kwargs": kwargs,
                "max_resources": max_resources,
                "status": "pending",
                "thread": None,
                "submitted_at": time.time()
            }
            
            # Start task thread
            thread = threading.Thread(
                target=self._run_task,
                args=(task_id,),
                daemon=True
            )
            self.tasks[task_id]["thread"] = thread
            self.tasks[task_id]["status"] = "starting"
            thread.start()
            
            return task_id
            
    def _run_task(self, task_id: str) -> None:
        
        task = self.tasks[task_id]
        task["status"] = "acquiring_resources"
        
        try:
            # Request initial resources
            initial_resources = {r: 1 for r in task["max_resources"]}
            if not self.resource_manager.request_resources(task_id, initial_resources):
                task["status"] = "failed"
                task["error"] = "Failed to acquire initial resources"
                return
                
            task["status"] = "running"
            
            # Execute the task function
            result = task["function"](
                *task["args"],
                resource_manager=self.resource_manager,
                task_id=task_id,
                **task["kwargs"]
            )
            
            # Store the result
            with self.lock:
                self.task_results[task_id] = {
                    "result": result,
                    "completed_at": time.time(),
                    "success": True
                }
                
            task["status"] = "completed"
            
        except Exception as e:
            # Handle task failure
            with self.lock:
                self.task_results[task_id] = {
                    "error": str(e),
                    "completed_at": time.time(),
                    "success": False
                }
                
            task["status"] = "failed"
            task["error"] = str(e)
            
        finally:
            # Release all resources
            self.resource_manager.remove_process(task_id)
            
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        
        with self.lock:
            if task_id not in self.tasks:
                return None
                
            task = self.tasks[task_id].copy()
            # Remove thread object from the copy
            task.pop("thread", None)
            
            # Add result if available
            if task_id in self.task_results:
                task["result"] = self.task_results[task_id]
                
            return task
            
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        
        with self.lock:
            result = []
            for task_id, task in self.tasks.items():
                task_copy = task.copy()
                task_copy.pop("thread", None)
                
                if task_id in self.task_results:
                    task_copy["result"] = self.task_results[task_id]
                    
                result.append(task_copy)
                
            return result
            
    def cancel_task(self, task_id: str) -> bool:
        
        with self.lock:
            if task_id not in self.tasks:
                return False
                
            task = self.tasks[task_id]
            if task["status"] in ["completed", "failed"]:
                return False
                
            # Mark task as cancelled
            task["status"] = "cancelled"
            
            # Release resources
            self.resource_manager.remove_process(task_id)
            
            # Note: We can't actually stop the thread, but we can mark it as cancelled
            # and release its resources
            
            return True
