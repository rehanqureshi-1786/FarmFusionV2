# Helper utilities for test suite meta‑analysis

import pkgutil
import importlib
import inspect
from typing import List

def discover_pytest_functions(package_name: str = "backend.tests") -> List[str]:
    """Recursively import all modules under ``package_name`` and collect the fully‑qualified
    names of callables that are pytest test functions (i.e. name starts with ``test_``).
    Returns a list of ``module_name.function_name`` strings.
    """
    discovered: List[str] = []
    package = importlib.import_module(package_name)
    for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=package_name + "."):
        if is_pkg:
            # Recurse into sub‑packages (e.g. data fixtures)
            discovered.extend(discover_pytest_functions(mod_name))
            continue
        try:
            module = importlib.import_module(mod_name)
        except Exception:
            continue
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and name.startswith("test_"):
                discovered.append(f"{mod_name}.{name}")
    return discovered

def count_pytest_cases() -> int:
    """Return the total number of discovered pytest test functions across the repository.
    This is a best‑effort count; if a module cannot be imported it is ignored.
    """
    return len(discover_pytest_functions())
