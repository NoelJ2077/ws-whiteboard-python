#/app/services/taskhandler.py
import inspect
from typing import Dict

from app.utils.logger import Logger
from app.services.Modulaufgaben import Modules

Log = Logger("app-services-taskhandler")
# // START (Task 2) & // END -> Ganze Klasse überarbeitet, loggt neu alle Funktionen beim starten der app + Dynamischer Modulimport 

class TaskHandler:
    """Handles all @prefix commands dynamically loaded from Modulaufgaben."""

    def __init__(self):
        self.handlers: Dict[str, callable] = {}
        self._load_namespaces(Modules)

    def _load_namespaces(self, modules: dict):
        """Iterate over all loaded modules and register async functions."""
        for module_name, module in modules.items():
            namespace = getattr(module, "__namespace__", None)
            if not namespace:
                Log.critical(f"Error: missing __namespace__ in module {module_name}")
                continue

            # Register all submodules/functions
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(module, attr_name)
                self._register_functions(namespace, attr)

    def _register_functions(self, namespace: str, module_or_func):
        """Registers all async functions from a module into handlers dict."""
        for name, obj in inspect.getmembers(module_or_func):
            if name.startswith("_"):
                continue
            if inspect.iscoroutinefunction(obj):
                key = f"{namespace.lower()}.{name.lower()}"
                if key in self.handlers:
                    Log.warning(f"Duplicate command key: {key}, skipping")
                    continue
                self.handlers[key] = obj
                Log.debug(f"Registered command: {key}")

    async def handle_execute_command(self, prefix: str, command: str, client_id: str, message: str = None, extras: dict = None):
        """Executes a registered async command with parameters."""
        key = f"{prefix.lower()}.{command.lower()}"
        handler = self.handlers.get(key)
        Log.info(f"Executing handler: {handler}")
        if not handler:
            Log.debug(f"Unknown command: {prefix}.{command}")
            return f"❌ Unknown {prefix} command: {command}"

        sig = inspect.signature(handler)
        kwargs = {}
        extras = extras or {}

        if "client_id" in sig.parameters:
            kwargs["client_id"] = client_id
        if "msg" in sig.parameters and message is not None:
            kwargs["msg"] = message
        for k, v in extras.items():
            if k in sig.parameters:
                kwargs[k] = v

        return await handler(**kwargs)
