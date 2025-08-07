import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.container import Container

class TestE2EWorkflow:
    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            local_data = base_path / "local_data"
            local_data.mkdir()
            state_file = base_path / "state.json"
            yield local_data, state_file

    @pytest.fixture
    def e2e_container(self, temp_dirs):
        local_data, state_file = temp_dirs
        config = {
            "app": {"state_file": str(state_file)},
            "ssh": {"host": "localhost", "port": 2222, "username": "test", "pool_size": 1},
            "paths": {"local_logdata": str(local_data), "remote_workspace": "/remote"},
            "resources": {"gpu_count": 2}
        }
        container = Container()
        container.config.from_dict(config)
        return container

    @patch('pynvml.nvmlInit', return_value=None) # Disable real GPU monitoring
    def test_full_workflow_from_scan_to_schedule(self, mock_nvml, e2e_container, temp_dirs):
        # Given
        local_data, _ = temp_dirs

        # Create a new case directory on the "local file system"
        new_case_id = "case_e2e_001"
        (local_data / new_case_id).mkdir()

        # Get the orchestrator from the real container
        orchestrator = e2e_container.workflow_orchestrator()

        # When
        # Run the main processing step
        orchestrator.process_new_cases()

        # Then
        # 1. Verify the case was added to the repository
        case_repo = e2e_container.case_repo()
        case = case_repo.get(new_case_id)
        assert case is not None
        assert case.case_id == new_case_id

        # 2. Verify that tasks were scheduled
        scheduler = e2e_container.task_scheduler()
        # The scheduler's queue should now have tasks for this case
        next_task = scheduler.get_next_task()
        assert next_task is not None
        assert next_task.job_id is not None # A job should have been created
        assert next_task.type.value == "upload"

        # Verify a job was created
        job_repo = e2e_container.job_repo()
        jobs = job_repo.list_all()
        assert len(jobs) == 1
        assert jobs[0].case_id == new_case_id
