#!/usr/bin/env python3
"""
Enhancement loader for IntermCLI tools.
Handles detection of optional dependencies and provides consistent
information about available enhancements.
"""
import importlib.util
import logging
import sys
from typing import Any, Callable, Dict, List, Optional


class EnhancementLoader:
    def __init__(self, tool_name: str, logger=None):
        """
        Initialize enhancement loader for a specific tool.

        Args:
            tool_name: Name of the tool
            logger: Optional logger (creates one if not provided)
        """
        self.tool_name = tool_name
        self.logger = logger or self._get_default_logger()
        self.dependencies: Dict[str, bool] = {}
        self.features: Dict[str, bool] = {}
        self._enhancement_callbacks: Dict[str, Callable] = {}

    def _get_default_logger(self):
        """Create a basic logger if none provided."""
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        return logging.getLogger(self.tool_name)

    def check_dependency(self, module_name: str, alias: Optional[str] = None) -> bool:
        """
        Check if a dependency is available and register it.

        Args:
            module_name: Name of the module to check
            alias: Optional alias to use for the dependency

        Returns:
            True if dependency is available, False otherwise
        """
        key = alias or module_name
        is_available = self._is_module_available(module_name)
        self.dependencies[key] = is_available
        return is_available

    def _is_module_available(self, module_name: str) -> bool:
        """Check if a module is available without importing it."""
        # Special case for tomllib (stdlib in Python 3.11+)
        if module_name == "tomllib" and sys.version_info >= (3, 11):
            return True

        # For all other modules, check if they can be imported
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError):
            return False

    def register_feature(self, feature_name: str, required_deps: List[str]) -> bool:
        """
        Register a feature and check if all its dependencies are available.

        Args:
            feature_name: Name of the feature
            required_deps: List of dependency names required for this feature

        Returns:
            True if feature is available, False otherwise
        """
        # Check that all dependencies are registered
        for dep in required_deps:
            if dep not in self.dependencies:
                self.logger.warning(
                    f"Dependency {dep} not registered before feature {feature_name}"
                )
                self.check_dependency(dep)

        is_available = all(self.dependencies.get(dep, False) for dep in required_deps)
        self.features[feature_name] = is_available
        return is_available

    def register_enhancement(
        self, feature_name: str, callback: Callable, required_deps: List[str]
    ) -> None:
        """
        Register an enhancement with a callback that will be called if available.

        Args:
            feature_name: Name of the feature
            callback: Function to call if feature is available
            required_deps: List of dependencies required for this feature
        """
        is_available = self.register_feature(feature_name, required_deps)
        if is_available:
            self._enhancement_callbacks[feature_name] = callback

    def apply_enhancements(self, **kwargs) -> Dict[str, Any]:
        """
        Apply all registered enhancements that are available.

        Args:
            **kwargs: Keyword arguments to pass to enhancement callbacks

        Returns:
            Dictionary of results from enhancement callbacks
        """
        results = {}
        for feature_name, callback in self._enhancement_callbacks.items():
            if self.features.get(feature_name, False):
                try:
                    results[feature_name] = callback(**kwargs)
                except Exception as e:
                    self.logger.error(f"Error applying enhancement {feature_name}: {e}")
                    results[feature_name] = None
        return results

    def get_missing_dependencies(self) -> List[str]:
        """
        Get a list of missing dependencies.

        Returns:
            List of missing dependency names
        """
        return [name for name, available in self.dependencies.items() if not available]

    def get_unavailable_features(self) -> List[str]:
        """
        Get a list of unavailable features.

        Returns:
            List of unavailable feature names
        """
        return [name for name, available in self.features.items() if not available]

    def print_status(self, show_features: bool = True, show_deps: bool = True) -> None:
        """
        Print the status of dependencies and features.

        Args:
            show_features: Whether to show feature status
            show_deps: Whether to show dependency status
        """
        if show_deps:
            self.logger.info(f"\nOptional Dependencies for {self.tool_name}:")
            for name, available in sorted(self.dependencies.items()):
                status = "✅ Available" if available else "❌ Missing"
                self.logger.info(f"  {name:15}: {status}")

        if show_features and self.features:
            self.logger.info("\nEnhanced Features:")
            for name, available in sorted(self.features.items()):
                status = "✅ Enabled" if available else "❌ Disabled"
                self.logger.info(f"  {name:20}: {status}")

        missing = self.get_missing_dependencies()
        if missing:
            self.logger.info("\nTo enable all features, install missing dependencies:")
            self.logger.info(f"  pip install {' '.join(missing)}")

    def get_rich_console(self) -> Optional[Any]:
        """Get Rich console if available, otherwise None."""
        if self.dependencies.get("rich", False):
            try:
                from rich.console import Console

                return Console()
            except ImportError:
                return None
        return None

    @staticmethod
    def check_common_dependencies() -> Dict[str, bool]:
        """
        Check common dependencies used across tools.

        Returns:
            Dictionary of dependency names to availability
        """
        common_deps = {
            "rich": False,
            "requests": False,
            "tomli": False,
            "urllib3": False,
            "click": False,
        }

        for dep in common_deps:
            try:
                common_deps[dep] = importlib.util.find_spec(dep) is not None
            except (ImportError, ValueError):
                common_deps[dep] = False

        # Special case for tomllib (stdlib in Python 3.11+)
        try:
            if sys.version_info >= (3, 11):
                # Check for tomllib without importing
                common_deps["tomllib"] = importlib.util.find_spec("tomllib") is not None
            else:
                # Check for tomli without importing
                common_deps["tomli"] = importlib.util.find_spec("tomli") is not None
        except (ImportError, ValueError):
            pass

        return common_deps


def check_dependencies(tool_name: str, dependencies: List[str]) -> Dict[str, bool]:
    """
    Helper function to check dependencies for a tool.

    Args:
        tool_name: Name of the tool
        dependencies: List of dependency names to check

    Returns:
        Dictionary of dependency names to availability
    """
    loader = EnhancementLoader(tool_name)
    for dep in dependencies:
        loader.check_dependency(dep)
    return loader.dependencies
