#!/usr/bin/env python3

# Standard library imports
import importlib.util
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure shared utilities are available (same as scan-ports.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    from shared.path_utils import require_shared_utilities

    require_shared_utilities()
except ImportError:
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Import shared utilities
from shared.config_loader import ConfigLoader


# Custom exception for manifest errors
class ManifestError(Exception):
    """Raised when the tools manifest is missing or malformed."""

    pass


# TOML loader selection
toml_loader = None
toml_loader_name = None
try:
    import tomllib

    toml_loader = tomllib
    toml_loader_name = "tomllib (builtin)"
except ImportError:
    try:
        import tomli

        toml_loader = tomli
        toml_loader_name = "tomli (external)"
    except ImportError:
        try:
            import toml

            toml_loader = toml
            toml_loader_name = "toml (external)"
        except ImportError:
            toml_loader = None
            toml_loader_name = None

# Suite version
SUITE_VERSION = "1.0.0"

# Module-level logger. Defined at import time so helper functions
# (get_tools_from_manifest, delegate_to_tool, ...) can log even when the module
# is imported rather than run as __main__. setup_logging() adjusts its level.
logger = logging.getLogger("intermcli")


# Logging setup
def get_global_config():
    """
    Load global config from ~/.config/intermcli/defaults.toml (TOML format).
    Returns a dict, or empty dict if not found or error.
    """
    config_path = Path.home() / ".config" / "intermcli" / "defaults.toml"
    if not config_path.exists() or not toml_loader:
        return {}
    try:
        if toml_loader_name in ["tomllib (builtin)", "tomli (external)"]:
            with open(config_path, "rb") as f:
                config = toml_loader.load(f)
        else:
            config = toml_loader.load(config_path)
        return config
    except Exception:
        return {}


def setup_logging():
    """
    Set up logging based on global config log_level.
    """
    config = get_global_config()
    log_level = config.get("log_level", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format="[%(levelname)s] %(message)s")
    logger.setLevel(numeric_level)
    return logger


# Manifest loader
def get_tools_from_manifest():
    """
    Load and parse the tools manifest. Raises ManifestError if missing or malformed.
    """
    # Use ConfigLoader to find and load the manifest file automatically
    # Minimal config/manifest loading using ConfigLoader
    config_loader = ConfigLoader("interm", logger)
    config = config_loader.load_config()
    manifest = None
    # Look for manifest in loaded config (merged from all sources)
    if "tools_manifest" in config:
        manifest = config["tools_manifest"]
    elif "tool" in config:
        manifest = config
    # If manifest is not found, raise error
    if manifest is None:
        logger.error("tools_manifest.toml not found in any config location.")
        raise ManifestError("tools_manifest.toml not found.")
    if "tool" in manifest:
        if isinstance(manifest["tool"], list):
            return manifest["tool"]
        elif isinstance(manifest["tool"], dict):
            return [v | {"name": k} for k, v in manifest["tool"].items()]
    tool_tables = []
    for k, v in manifest.items():
        if isinstance(v, dict) and "description" in v:
            entry = v.copy()
            entry["name"] = k
            tool_tables.append(entry)
    if tool_tables:
        return tool_tables
    raise ManifestError("No valid tool entries found in manifest.")


# CLI help
def show_suite_help():
    print(f"IntermCLI Suite v{SUITE_VERSION}")
    print("Usage:")
    print("  interm list         Show available tools")
    print("  interm version      Show suite version")
    print("  interm about        Project info, docs, installation")
    print("  interm status       Show tool install status and optional dependencies")


# CLI command handler
def handle_suite_command(command, args):
    if command == "list":
        try:
            tools = get_tools_from_manifest()
        except ManifestError as e:
            logger.error(str(e))
            return
        if not tools:
            logger.warning("No tools found or unable to read manifest.")
            return
        print("Available tools:")
        for tool in tools:
            name = tool.get("name", "")
            desc = tool.get("description", "")
            if desc:
                print(f"  {name:15} - {desc}")
            else:
                print(f"  {name}")
    elif command == "version":
        print(f"IntermCLI Suite version {SUITE_VERSION}")
    elif command == "about":
        print(f"IntermCLI Suite v{SUITE_VERSION}")
        print("Project: https://github.com/pdbeard/intermcli")
        print("Installation: ./install.sh or see README.md")
        print("Documentation: docs/ and https://github.com/pdbeard/intermcli/docs")
        print("Each tool has its own config file. See tool docs for details.")
    elif command == "status":
        show_status()
    else:
        show_suite_help()


# Status command
def show_status():
    """
    Print the status of all tools and their optional dependencies.
    """
    try:
        tools = get_tools_from_manifest()
    except ManifestError as e:
        logger.error(str(e))
        return
    if not tools:
        logger.warning("No tools found or unable to read manifest.")
        return
    print(f"IntermCLI Suite Status (v{SUITE_VERSION})")
    print("Tool                Installed   Optional Dependencies")
    print("------------------------------------------------------")
    missing_deps = set()
    for tool in tools:
        name = tool.get("name", "")
        # desc = tool.get("description", "")
        opt_deps = tool.get("optional_deps", [])
        exe = find_tool_executable(name)
        installed = "✅" if exe and os.path.exists(exe) else "❌"
        dep_status = []
        for dep in opt_deps:
            found = importlib.util.find_spec(dep) is not None
            dep_status.append(f"{dep}{' ✓' if found else ' ✗'}")
            if not found:
                missing_deps.add(dep)
        dep_str = ", ".join(dep_status) if dep_status else "-"
        print(f"{name:20} {installed:9}  {dep_str}")
    if missing_deps:
        print("\nUninstalled optional dependencies:")
        print("  " + ", ".join(sorted(missing_deps)))
    else:
        print("\nAll optional dependencies are installed.")


# Tool executable lookup
def find_tool_executable(tool_name):
    """
    Find the executable for a tool, searching ~/.local/bin and then PATH.
    Returns the path or None if not found.
    """
    local_bin = Path.home() / ".local" / "bin" / tool_name
    if local_bin.exists():
        return str(local_bin)
    exe = shutil.which(tool_name)
    return exe


def tool_exists(tool_name):
    return find_tool_executable(tool_name) is not None


# Tool delegation
def delegate_to_tool(tool_name, args):
    """
    Delegate CLI args to a tool executable, running as a Python script if needed.
    """
    tool_path = find_tool_executable(tool_name)
    if not tool_path or not os.path.exists(tool_path):
        logger.error(
            f"❌ Tool '{tool_name}' not found. Hint: Ensure it is installed and in ~/.local/bin or your PATH."
        )
        sys.exit(1)
    if tool_path.endswith(".py"):
        cmd = [sys.executable, tool_path] + args
    else:
        cmd = [tool_path] + args
    subprocess.run(cmd)


# Main entry point
def main():
    if len(sys.argv) < 2:
        show_suite_help()
        return

    command = sys.argv[1]
    if command in ["list", "version", "about", "status"]:
        handle_suite_command(command, sys.argv[2:])
    elif command in ("-h", "--help", "help"):
        show_suite_help()
    else:
        # Treat the command as a tool name and delegate to it.
        try:
            tools = get_tools_from_manifest()
            tool_names = {t.get("name") for t in tools}
        except ManifestError:
            tool_names = set()

        if command in tool_names:
            delegate_to_tool(command, sys.argv[2:])
        else:
            logger.error(f"Unknown command or tool: {command}")
            show_suite_help()


if __name__ == "__main__":

    setup_logging()
    main()
