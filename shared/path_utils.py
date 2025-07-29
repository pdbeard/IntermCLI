#!/usr/bin/env python3
"""
IntermCLI path utilities.
Ensures shared modules can be imported properly by tools.
"""

import importlib.util
import sys
from pathlib import Path


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
