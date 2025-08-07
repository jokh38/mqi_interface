import pytest
import yaml
from pathlib import Path
from unittest.mock import mock_open, patch

from src.infrastructure.config import ConfigManager, ConfigurationError

# Tests
class TestConfigManager:
    @pytest.fixture
    def valid_config_data(self):
        return {"app": {"name": "MQI Communicator", "version": "2.0.0"}}

    @pytest.fixture
    def valid_config_yaml(self, valid_config_data):
        return yaml.dump(valid_config_data)

    def test_load_valid_config(self, valid_config_yaml):
        # Given
        mock_file = mock_open(read_data=valid_config_yaml)
        with patch("pathlib.Path.is_file", return_value=True), \
             patch("builtins.open", mock_file):

            # When
            manager = ConfigManager(Path("dummy/path/config.yaml"))

            # Then
            assert manager.get("app")["name"] == "MQI Communicator"
            assert manager.get("app")["version"] == "2.0.0"

    def test_config_file_not_found(self):
        # Given
        with patch("pathlib.Path.is_file", return_value=False):

            # When / Then
            with pytest.raises(ConfigurationError, match="Configuration file not found"):
                ConfigManager(Path("non/existent/path/config.yaml"))

    def test_invalid_yaml_format(self):
        # Given
        invalid_yaml = "app: name: MQI\n  version: 2.0" # incorrect indentation
        mock_file = mock_open(read_data=invalid_yaml)

        with patch("pathlib.Path.is_file", return_value=True), \
             patch("builtins.open", mock_file):

            # When / Then
            with pytest.raises(ConfigurationError, match="Error parsing YAML file"):
                ConfigManager(Path("dummy/path/config.yaml"))

    def test_get_value(self, valid_config_yaml):
        # Given
        mock_file = mock_open(read_data=valid_config_yaml)
        with patch("pathlib.Path.is_file", return_value=True), \
             patch("builtins.open", mock_file):
            manager = ConfigManager(Path("dummy/path/config.yaml"))

            # When
            app_config = manager.get("app")

            # Then
            assert app_config is not None
            assert app_config["name"] == "MQI Communicator"

    def test_get_non_existent_key(self, valid_config_yaml):
        # Given
        mock_file = mock_open(read_data=valid_config_yaml)
        with patch("pathlib.Path.is_file", return_value=True), \
             patch("builtins.open", mock_file):
            manager = ConfigManager(Path("dummy/path/config.yaml"))

            # When
            result = manager.get("non_existent_key")

            # Then
            assert result is None

    def test_get_with_default_value(self, valid_config_yaml):
        # Given
        mock_file = mock_open(read_data=valid_config_yaml)
        with patch("pathlib.Path.is_file", return_value=True), \
             patch("builtins.open", mock_file):
            manager = ConfigManager(Path("dummy/path/config.yaml"))

            # When
            result = manager.get("non_existent_key", "default_value")

            # Then
            assert result == "default_value"
