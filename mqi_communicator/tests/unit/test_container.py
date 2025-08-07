import pytest
from unittest.mock import patch

from src.container import Container

class TestContainer:
    @pytest.fixture
    def sample_config(self):
        return {
            "app": {
                "state_file": "/tmp/test_state.json"
            },
            "ssh": {
                "host": "localhost",
                "port": 2222,
                "username": "test",
                "key_file": "/path/to/key",
                "pool_size": 2
            },
            "paths": {
                "local_logdata": "/local/data",
                "remote_workspace": "/remote/workspace"
            },
            "resources": {
                "gpu_count": 4
            }
        }

    @patch('pynvml.nvmlInit', return_value=None) # Prevent NVML init during test
    def test_container_wiring_and_resolution(self, mock_nvml, sample_config):
        # Given
        container = Container()
        container.config.from_dict(sample_config)

        # When
        container.wire(modules=[__name__]) # Wire to the current module

        # Then
        orchestrator = container.workflow_orchestrator()

        assert orchestrator is not None
        assert orchestrator._case_service is not None
        assert orchestrator._task_scheduler is not None

        # Clean up
        container.unwire()
