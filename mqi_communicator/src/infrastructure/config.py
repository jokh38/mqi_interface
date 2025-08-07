import yaml
from pathlib import Path

class ConfigurationError(Exception):
    pass

class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.is_file():
            raise ConfigurationError(f"Configuration file not found at {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML file: {e}")

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
