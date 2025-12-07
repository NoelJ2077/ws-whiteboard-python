#/app/services/taskhandler.py
import inspect
from typing import Dict

from app.utils.logger import Logger
from app.services.Modulaufgaben import Server, Client, Serveradmin, Server_Info

__namespaces__ = Server, Client, Serveradmin, Server_Info
Log = Logger("app-services-taskhandler")

# // START (Task 2) & // END -> Ganze Klasse überarbeitet, loggt neu alle Funktionen beim starten der app.
class TaskHandler:
    """All @prefix inputs are handled here. Each namespace module provides async functions
    that can be called via @prefix <command>."""

    def __init__(self):
        self.handlers: Dict[str, callable] = {}
        self._load_namespaces(__namespaces__)
    
    def _load_namespaces(self, namespaces):
        # get all @modul <method> from all modules from Modulaufgaben 
        for package in namespaces:
            namespace = getattr(package, "__namespace__", None)
            if not namespace:
                Log.critical(f"Error while init TaskHandler: missing __namespace__ in {package}")
                continue

            for attr_name in dir(package):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(package, attr_name)
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
                Log.debug(f"Registered [@module.cmd] : {key}") # logging all callable functions. 

    async def handle_execute_command(self, prefix: str, command: str, client_id: str, message: str = None, extras: dict = None):
        """ Handle execution with all parameters passed.  """
        key = f"{prefix.lower()}.{command.lower()}"
        handler = self.handlers.get(key)
        Log.info(f"handel exec: {handler}")
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

        # pass extra parameter. 
        for k, v in extras.items():
            if k in sig.parameters:
                kwargs[k] = v

        return await handler(**kwargs)



    
