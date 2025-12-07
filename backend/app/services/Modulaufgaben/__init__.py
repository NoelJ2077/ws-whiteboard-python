# app/services/Modulaufgaben/init
import os, importlib

Modules = {}
Namespaces = []

package_dir = os.path.dirname(__file__)

for item in os.listdir(package_dir):
    full_path = os.path.join(package_dir, item)

    # Only load subdirectories that are modules
    if os.path.isdir(full_path) and "__init__.py" in os.listdir(full_path):
        module_name = f"{__name__}.{item}"
        module = importlib.import_module(module_name)
        Modules[item] = module

        namespace = getattr(module, "__namespace__", None)
        if namespace:
            Namespaces.append(namespace)

__all__ = ["Modules", "Namespaces"]
