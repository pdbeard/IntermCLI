#!/usr/bin/env python3
"""
Configuration loader for IntermCLI tools.
Handles TOML loading with proper precedence:
1. Command line arguments
2. Environment variables
3. Project-level config (.intermcli.toml)
4. User tool-specific config (~/.config/intermcli/{tool}.toml)
5. User global config (~/.config/intermcli/config.toml)
6. Tool default config (tools/{tool}/config/defaults.toml)
7. Built-in defaults
"""
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# TOML support with fallback
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomli_lib  # type: ignore # Fallback for older Python

        tomllib = tomli_lib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore # Will raise appropriate error during usage


class ConfigLoader:
    def __init__(self, tool_name: str, logger: Optional[logging.Logger] = None) -> None:
        """Initialize config loader for a specific tool."""
        self.tool_name = tool_name
        self.logger = logger or self._get_default_logger()
        self.config: Dict[str, Any] = {}
        self.config_source: str = "built-in defaults"
        self.has_toml = tomllib is not None

    def _get_default_logger(self) -> logging.Logger:
        """Create a basic logger if none provided."""
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        return logging.getLogger(self.tool_name)

    def load_config(self, cmd_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load configuration with proper precedence.

        Args:
            cmd_args: Optional dictionary of command line arguments to override config

        Returns:
            Dict containing merged configuration
        """
        # Check TOML support
        if not tomllib:
            self.logger.warning("TOML support not available")
            self.logger.info("Install tomli for Python < 3.11: pip3 install tomli")
            return self._get_default_config()

        # Start with built-in defaults
        config = self._get_default_config()

        # Try loading from files in precedence order (low to high)
        config_files = self._get_config_files()
        for file_path, desc in config_files:
            if file_path.exists():
                try:
                    with open(file_path, "rb") as f:
                        file_config = tomllib.load(f)

                    # Update config with file values
                    self._deep_update(config, file_config)
                    self.config_source = str(file_path)
                    self.logger.debug(f"Loaded config from {file_path}")
                except Exception as e:
                    self.logger.error(f"Error loading config from {file_path}: {e}")

        # Apply environment variable overrides
        self._apply_env_overrides(config)

        # Apply command line argument overrides if provided
        if cmd_args:
            self._apply_cmd_args(config, cmd_args)

        self.config = config
        return config

    def _get_config_files(self) -> List[Tuple[Path, str]]:
        """Get config files in precedence order (lowest to highest)."""
        home_dir = Path.home()
        config_dir = home_dir / ".config" / "intermcli"
        script_path = Path(sys.argv[0]).resolve()

        # Find the tool directory by scanning for the expected structure
        base_dir = script_path.parent
        if base_dir.name == self.tool_name:
            tool_dir = base_dir
        else:
            # Try to find it in the typical location
            project_root = self._find_project_root(script_path)
            if project_root:
                tool_dir = project_root / "tools" / self.tool_name.replace("-", "_")
                if not tool_dir.exists():
                    tool_dir = project_root / "tools" / self.tool_name
            else:
                # Fall back to relative from script
                tool_dir = script_path.parent

        return [
            (tool_dir / "config" / "defaults.toml", "Tool defaults"),
            (config_dir / "config.toml", "User global config"),
            (config_dir / f"{self.tool_name}.toml", "User tool-specific config"),
            (Path.cwd() / ".intermcli.toml", "Project config"),
        ]

    def _find_project_root(self, start_path: Path) -> Optional[Path]:
        """Find the project root by looking for markers like shared/ directory."""
        current = start_path
        for _ in range(5):  # Limit the depth of search
            if current.name == "intermCLI" or (current / "shared").exists():
                return current
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        return None

    def _get_default_config(self) -> Dict[str, Any]:
        """Get built-in default configuration."""
        return {
            "version": "1.0.0",
            "common": {
                "timeout": 30,
                "dry_run": False,
                "output_format": "auto",
                "verbose": False,
                "color": "auto",
            },
        }

    def _deep_update(
        self, base_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> None:
        """Deep update configuration dictionary."""
        for key, value in new_config.items():
            if (
                isinstance(value, dict)
                and key in base_config
                and isinstance(base_config[key], dict)
            ):
                self._deep_update(base_config[key], value)
            else:
                base_config[key] = value

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides to config."""
        prefix = f"INTERMCLI_{self.tool_name.upper().replace('-', '_')}_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()
                # Convert nested keys (e.g., COMMON_TIMEOUT -> common.timeout)
                if "_" in config_key:
                    parts = config_key.split("_")
                    section = config
                    for part in parts[:-1]:
                        if part not in section:
                            section[part] = {}
                        section = section[part]
                    section[parts[-1]] = self._convert_env_value(value)
                else:
                    config[config_key] = self._convert_env_value(value)

    def _apply_cmd_args(self, config: Dict[str, Any], cmd_args: Dict[str, Any]) -> None:
        """Apply command line argument overrides to config."""
        # Add command line arguments to config, skipping None values
        for key, value in cmd_args.items():
            if value is not None:
                # Handle nested keys with dots
                if "." in key:
                    parts = key.split(".")
                    section = config
                    for part in parts[:-1]:
                        if part not in section:
                            section[part] = {}
                        section = section[part]
                    section[parts[-1]] = value
                else:
                    config[key] = value

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Handle boolean values
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # Handle numeric values
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            # Return as string for non-numeric values
            return value

    def get_config(self) -> Dict[str, Any]:
        """Get loaded configuration or load if not already loaded."""
        if not self.config:
            return self.load_config()
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value with optional default.

        Args:
            key: Configuration key (can use dots for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        config = self.get_config()
        if "." in key:
            parts = key.split(".")
            current = config
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    return default
                current = current[part]
            return current
        return config.get(key, default)

    def show_config_source(self) -> str:
        """Get the source of the loaded configuration."""
        return self.config_source

    def add_config_file(self, file_path: Union[str, Path]) -> None:
        """
        Add a specific config file to be loaded.

        Args:
            file_path: Path to the config file to add
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        if not path.exists():
            self.logger.warning(f"Config file not found: {path}")
            return

        try:
            if not self.has_toml:
                self.logger.warning(
                    "TOML support not available, cannot load config file"
                )
                return

            with open(path, "rb") as f:
                file_config = tomllib.load(f)

            # Update config with file values
            self._deep_update(self.config, file_config)
            self.config_source = str(path)
            self.logger.debug(f"Added config from {path}")
        except Exception as e:
            self.logger.error(f"Error loading config from {path}: {e}")


def load_config(
    tool_name: str, cmd_args: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Helper function to load config for a tool.

    Args:
        tool_name: Name of the tool
        cmd_args: Optional dictionary of command line arguments

    Returns:
        Merged configuration dictionary
    """
    loader = ConfigLoader(tool_name)
    return loader.load_config(cmd_args)
