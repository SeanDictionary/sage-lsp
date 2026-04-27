import configparser
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from pygls.workspace import Workspace

import pycodestyle

log = logging.getLogger(__name__)


class StyleConfig:
    """Unified configuration for pycodestyle and autopep8."""

    SECTIONS_KEYS = {
        "pycodestyle": [
            "select",
            "ignore",
            "exclude",
            "max_line_length",
            "indent_size",
            "hang_closing",
            "experimental",
            "aggressive",
        ],
        "autopep8": [
            "select",
            "ignore",
            "exclude",
            "max_line_length",
            "indent_size",
            "hang_closing",
            "experimental",
            "aggressive",
        ],
        "notebook": [
            "ignore",
        ]
    }
    SECTIONS = list(SECTIONS_KEYS.keys())

    def __init__(self, workspace: Workspace = None):
        self.workspace = workspace
        self.workspace_root = Path(workspace.root_path) if workspace.root_path else None
        self._config = self._load_config()
    
    def _merge_configs(self, *configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Merge multiple configuration dictionaries, with later ones taking precedence."""
        merged: Dict[str, Dict[str, Any]] = {}
        for config in configs:
            for section, settings in config.items():
                if section not in merged:
                    merged[section] = {}
                merged[section].update(settings)
        return merged

    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        """Load and merge global and project configurations."""
        # Load global config
        global_config = self._load_global_config()
        if global_config:
            log.debug(f"Loaded global config: {global_config}")

        # Load project config (overrides global)
        project_config = {}
        if self.workspace_root:
            project_config = self._load_project_config()
            if project_config:
                log.debug(f"Loaded project config: {project_config}")

        return self._merge_configs(global_config, project_config)

    def _load_global_config(self) -> Dict[str, Dict[str, Any]]:
        """Load global pycodestyle configuration from ~/.config/pycodestyle."""
        config_path = Path(pycodestyle.USER_CONFIG)
        return self._parse_config_file(config_path)

    def _load_project_config(self) -> Dict[str, Dict[str, Any]]:
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
            if any(config.values()):
                log.info(f"Using project config from {config_file}")
                return config

        return {}

    def _parse_config_file(self, config_path: Path) -> Dict[str, Dict[str, Any]]:
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
        
        for section in self.SECTIONS:
            section_config = {}
            if parser.has_section(section):
                for _key, value in parser.items(section):
                    key = _key.replace("-", "_")  # Normalize keys to match our expected format
                    if key in self.SECTIONS_KEYS[section]:
                        section_config[key] = self._parse_config_value(key, value)
            config[section] = section_config

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
        config = self._config.get("pycodestyle", {}).copy()

        return config

    def get_autopep8_config(self, line_range: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get configuration for autopep8.fix_code."""
        config = self._config.get("autopep8", {}).copy()
        if not config:
            # Fallback to pycodestyle config if autopep8 config is not defined
            config = self._config.get("pycodestyle", {}).copy()
        
        # Add line range if provided
        if line_range is not None:
            config["line_range"] = line_range
        
        return config
    
    def get_notebook_pycodestyle_config(self) -> Dict[str, Any]:
        """Get configuration for notebook formatting."""
        config = self.get_pycodestyle_config()
        notebook_config = self._config.get("notebook", {}).copy()

        for key in self.SECTIONS_KEYS["notebook"]:
            tmp = [
                *config.get(key, []),
                *notebook_config.get(key, []),
            ]
            if tmp:
                config[key] = tmp

        return config

    def get_notebook_autopep8_config(self, line_range: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get configuration for notebook formatting."""
        config = self.get_autopep8_config(line_range=line_range)
        notebook_config = self._config.get("notebook", {}).copy()

        for key in self.SECTIONS_KEYS["notebook"]:
            tmp = [
                *config.get(key, []),
                *notebook_config.get(key, []),
            ]
            if tmp:
                config[key] = tmp

        return config

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        """Get raw merged configuration."""
        return self._config.copy()