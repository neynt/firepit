import glob
import importlib
import os

def load_modules(directory):
    """Uses glob and importlib to import all the modules from a directory."""
    modules = {}
    module_paths = glob.glob(os.path.join(os.path.dirname(__file__), directory, '*.py'))
    for module_path in module_paths:
        module_name = module_path[:-3].split('/')[-1]
        module = importlib.import_module(f'{directory}.{module_name}')
        modules[module_name] = module
    return modules

COMMANDS = load_modules('commands')
