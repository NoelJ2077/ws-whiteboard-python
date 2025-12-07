# app/services/Modulaufgaben/Serveradmin/__init__.py
import os
import importlib

__namespace__ = "serveradmin"
""" Messages that go only to current admin.  """
__doc__ = f"Namespace Serveradmin for all @serveradmin <method>'s in the folder. Each method may be in 1 file.py"

# get all scripts in dir
package_dir = os.path.dirname(__file__)
__all__ = []

for filename in os.listdir(package_dir):
    if filename.endswith(".py") and filename not in ("__init__.py",):
        module_name = filename[:-3]
        importlib.import_module(f"{__name__}.{module_name}")
        __all__.append(module_name)
