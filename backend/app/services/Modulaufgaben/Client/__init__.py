# app/services/Modulaufgaben/Client/__init__.py
import os
import importlib

__namespace__ = "client"
__doc__ = f"Namespace Client for all @client <method>'s in the folder. Each method may be in 1 file.py"

package_dir = os.path.dirname(__file__)
__all__ = []

for filename in os.listdir(package_dir):
    if filename.endswith(".py") and filename not in ("__init__.py",):
        module_name = filename[:-3]
        importlib.import_module(f"{__name__}.{module_name}")
        __all__.append(module_name)
