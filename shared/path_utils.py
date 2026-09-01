#!/usr/bin/env python3
"""
IntermCLI path utilities.
Ensures shared modules can be imported properly by tools.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any


def add_shared_path() -> None:
    """
    Add the shared module directory to the Python path.
    This allows tools to import shared modules regardless of how they're invoked.
    """
    # Get the path to the intermCLI root directory
    root_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root_dir))


def ensure_shared_imports() -> bool:
    """
    Ensure shared modules can be imported, adding path if necessary.
    Returns:
        bool: True if imports are available, False otherwise
    """
    try:
        # Check if shared module is available without importing it
        if importlib.util.find_spec("shared") is not None:
            return True
    except ImportError:
        pass

    # If import fails, add path and try again
    add_shared_path()
    try:
        return importlib.util.find_spec("shared") is not None
    except ImportError:
        return False


def require_shared_utilities() -> None:
    """
    Ensure shared utilities are available or exit with a helpful message.
    """
    if not ensure_shared_imports():
        print("Error: This tool requires the IntermCLI shared utilities.")
        print("Please make sure the IntermCLI suite is properly installed.")
        print(
            "Run 'install.sh' from the IntermCLI root directory to set up the environment."
        )
        sys.exit(1)


def load_tool_lib_module(tool_file: str, tool_name: str, module_name: str) -> Any:
    """
    Import a module from a tool's own lib/ directory.

    Tool libraries live at ``tools/<tool>/lib/`` in a source checkout and at
    ``<install dir>/tool_libs/<tool>/`` once install.sh has copied them next to
    the installed tool scripts. Modules are loaded by file path so libraries
    belonging to different tools cannot collide on a top-level package name.

    Args:
        tool_file: The tool's ``__file__``
        tool_name: Directory name of the tool, e.g. "scan-ports"
        module_name: Module to load from the tool's lib directory

    Returns:
        The imported module

    Raises:
        ImportError: If the module cannot be found in any known location
    """
    cache_key = f"_intermcli_toollib.{tool_name}.{module_name}"
    cached = sys.modules.get(cache_key)
    if cached is not None:
        return cached

    tool_dir = Path(tool_file).resolve().parent
    candidates = [
        tool_dir / "lib" / f"{module_name}.py",
        tool_dir / "tool_libs" / tool_name / f"{module_name}.py",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location(cache_key, path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[cache_key] = module
        spec.loader.exec_module(module)
        return module

    raise ImportError(
        f"Could not locate '{module_name}' for tool '{tool_name}'. "
        f"Looked in: {', '.join(str(p) for p in candidates)}"
    )
