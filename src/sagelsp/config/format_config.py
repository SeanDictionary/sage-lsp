import configparser
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from pygls.workspace import Workspace

import pycodestyle

log = logging.getLogger(__name__)


class StyleConfig:
    """Unified configuration for pycodestyle and autopep8."""

    def __init__(self, workspace: Workspace = None):
        self.workspace = workspace
        self.workspace_root = Path(workspace.root_path) if workspace.root_path else None
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and merge global and project configurations."""
        config = {}

        # Load global config
        global_config = self._load_global_config()
        if global_config:
            config.update(global_config)
            log.debug(f"Loaded global config: {global_config}")

        # Load project config (overrides global)
        if self.workspace_root:
            project_config = self._load_project_config()
            if project_config:
                config.update(project_config)
                log.debug(f"Loaded project config: {project_config}")

        return config

    def _load_global_config(self) -> Dict[str, Any]:
        """Load global pycodestyle configuration from ~/.config/pycodestyle."""
        config_path = Path(pycodestyle.USER_CONFIG)
        return self._parse_config_file(config_path)

    def _load_project_config(self) -> Dict[str, Any]:
        """Load project configuration from setup.cfg, tox.ini, or .pycodestyle."""
        if not self.workspace_root:
            return {}

        # Check common config files in order of precedence
        config_files = [
            self.workspace_root / ".pycodestyle",
            self.workspace_root / "setup.cfg",
            self.workspace_root / "tox.ini",
        ]

        for config_file in config_files:
            config = self._parse_config_file(config_file)
            if config:
                log.info(f"Using project config from {config_file}")
                return config

        return {}

    def _parse_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Parse a pycodestyle configuration file."""
        if not config_path.exists():
            return {}

        parser = configparser.ConfigParser()
        try:
            parser.read(config_path)
        except Exception as e:
            log.warning(f"Failed to parse config file {config_path}: {e}")
            return {}

        config = {}
        
        section = "pycodestyle"
        if parser.has_section(section):
            for key, value in parser.items(section):
                config[key] = self._parse_config_value(key, value)

        return config

    def _parse_config_value(self, key: str, value: str) -> Any:
        """Parse configuration value to appropriate type."""
        # List values (comma-separated)
        if key in ["select", "ignore", "exclude"]:
            return [item.strip() for item in value.split(",") if item.strip()]
        
        # Integer values
        if key in ["max_line_length", "indent_size", "aggressive"]:
            try:
                return int(value)
            except ValueError:
                log.warning(f"Invalid integer value for {key}: {value}")
                return None
        
        # Boolean values
        if key in ["hang_closing", "experimental"]:
            return value.lower() in ("true", "1", "yes", "on")
        
        # String values
        return value

    def get_pycodestyle_config(self) -> Dict[str, Any]:
        """Get configuration for pycodestyle.StyleGuide."""
        config = {}
        
        # Map config keys to pycodestyle parameters
        key_mapping = {
            "select": "select",
            "ignore": "ignore",
            "exclude": "exclude",
            "max_line_length": "max_line_length",
            "indent_size": "indent_size",
            "hang_closing": "hang_closing",
        }
        
        for config_key, param_key in key_mapping.items():
            if config_key in self._config and self._config[config_key] is not None:
                config[param_key] = self._config[config_key]
        
        return config

    def get_autopep8_config(self, line_range: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get configuration for autopep8.fix_code."""
        config = {}
        
        # Map config keys to autopep8 parameters
        key_mapping = {
            "select": "select",
            "ignore": "ignore",
            "exclude": "exclude",
            "max_line_length": "max_line_length",
            "indent_size": "indent_size",
            "hang_closing": "hang_closing",
            "aggressive": "aggressive",
        }
        
        for config_key, param_key in key_mapping.items():
            if config_key in self._config and self._config[config_key] is not None:
                config[param_key] = self._config[config_key]
        
        # Add line range if provided
        if line_range is not None:
            config["line_range"] = line_range
        
        return config

    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw merged configuration."""
        return self._config.copy()