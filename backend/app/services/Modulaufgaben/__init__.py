# app/services/modulaufgaben/init
import os, importlib
# // START (Task 2) -> neue importlogik aller Module. Neue Module für Aufgabe 2:
# /Serveradmin: ('@serveradmin')
# /Server_Info: ('@server-info')

Modules = {}
Namespaces = []
__all__ = ["Modules", "Namespaces"]

package_dir = os.path.dirname(__file__)

for item in os.listdir(package_dir):
    full_path = os.path.join(package_dir, item)

    # Only load subpackages that contain an __init__.py
    if os.path.isdir(full_path) and "__init__.py" in os.listdir(full_path):
        module_name = f"{__name__}.{item}"
        module = importlib.import_module(module_name)

        Modules[item] = module

        if hasattr(module, "__namespace__"):
            Namespaces.append(module.__namespace__)
            
# // END (Task 2)
