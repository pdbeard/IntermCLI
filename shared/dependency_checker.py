#!/usr/bin/env python3
"""
DependencyChecker for IntermCLI tools.
Handles detection and reporting of optional dependencies using a manifest.
"""
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Dict


class DependencyChecker:
    def __init__(self, tool_name: str, logger=None):
        self.tool_name = tool_name
        self.logger = logger or self._get_default_logger()
        self.dependencies: Dict[str, bool] = {}
        # Load dependency manifest from config
        from shared.config_loader import ConfigLoader

        manifest_path = (
            Path(__file__).resolve().parents[1] / "config" / "dependency_manifest.toml"
        )
        self.manifest = {}
        try:
            loader = ConfigLoader(tool_name, self.logger)
            loader.add_config_file(manifest_path)
            self.manifest = loader.get("dependencies", {})
        except Exception as e:
            self.logger.warning(f"Could not load dependency manifest: {e}")

    def _get_default_logger(self):
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        return logging.getLogger(self.tool_name)

    def check_dependency(self, dep_key: str) -> bool:
        dep = self.manifest.get(dep_key, {})
        import_name = dep.get("import", dep_key)
        is_available = self._is_module_available(import_name)
        self.dependencies[dep_key] = is_available
        return is_available

    def _is_module_available(self, module_name: str) -> bool:
        if module_name == "tomllib" and sys.version_info >= (3, 11):
            return True
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError):
            return False

    def check_and_report_dependencies(self, dep_keys: list, output=None):
        for dep_key in dep_keys:
            self.check_dependency(dep_key)
        if output and hasattr(output, "print_key_value_section"):
            dependencies = {
                self.manifest.get(key, {}).get("description", key): (
                    "Available" if available else "Missing"
                )
                for key, available in self.dependencies.items()
            }
            output.print_key_value_section(
                f"Optional Dependencies for {self.tool_name}", dependencies
            )
            missing = [k for k, v in self.dependencies.items() if not v]
            missing_pkgs = [
                self.manifest.get(dep, {}).get("package", dep) for dep in missing
            ]
            if missing_pkgs:
                output.info("\nTo enable all features, install missing dependencies:")
                if hasattr(output, "print_list"):
                    install_commands = [f"pip install {pkg}" for pkg in missing_pkgs]
                    output.print_list("Install Commands", install_commands)
                else:
                    output.info(f"  pip install {' '.join(missing_pkgs)}")
        else:
            for key, available in self.dependencies.items():
                desc = self.manifest.get(key, {}).get("description", key)
                status = "Available" if available else "Missing"
                self.logger.info(f"{desc}: {status}")
            missing = [k for k, v in self.dependencies.items() if not v]
            if missing:
                pkgs = [
                    self.manifest.get(dep, {}).get("package", dep) for dep in missing
                ]
                self.logger.info(
                    f"To enable all features, install: pip install {' '.join(pkgs)}"
                )


# def check_dependencies(tool_name: str, dependencies: List[str]) -> Dict[str, bool]:
#     """
#     Helper function to check dependencies for a tool.

#     Args:
#         tool_name: Name of the tool
#         dependencies: List of dependency names to check

#     Returns:
#         Dictionary of dependency names to availability
#     """
#     loader = EnhancementLoader(tool_name)
#     for dep in dependencies:
#         loader.check_dependency(dep)
#     return loader.dependencies
