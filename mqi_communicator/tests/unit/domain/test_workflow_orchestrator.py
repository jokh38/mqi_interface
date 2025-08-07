import pytest
from unittest.mock import MagicMock

from src.services.interfaces import ICaseService
from src.domain.interfaces import ITaskScheduler

from src.domain.workflow_orchestrator import WorkflowOrchestrator

class TestWorkflowOrchestrator:
    @pytest.fixture
    def mock_case_service(self) -> MagicMock:
        return MagicMock(spec=ICaseService)

    @pytest.fixture
    def mock_task_scheduler(self) -> MagicMock:
        return MagicMock(spec=ITaskScheduler)

    @pytest.fixture
    def orchestrator(self, mock_case_service, mock_task_scheduler) -> WorkflowOrchestrator:
        return WorkflowOrchestrator(
            case_service=mock_case_service,
            task_scheduler=mock_task_scheduler
        )

    def test_process_new_cases_schedules_found_cases(self, orchestrator, mock_case_service, mock_task_scheduler):
        # Given
        mock_case_service.scan_for_new_cases.return_value = ["case1", "case2"]

        # When
        orchestrator.process_new_cases()

        # Then
        mock_case_service.scan_for_new_cases.assert_called_once()
        assert mock_task_scheduler.schedule_case.call_count == 2
        mock_task_scheduler.schedule_case.assert_any_call("case1")
        mock_task_scheduler.schedule_case.assert_any_call("case2")

    def test_process_new_cases_does_nothing_when_none_found(self, orchestrator, mock_case_service, mock_task_scheduler):
        # Given
        mock_case_service.scan_for_new_cases.return_value = []

        # When
        orchestrator.process_new_cases()

        # Then
        mock_case_service.scan_for_new_cases.assert_called_once()
        mock_task_scheduler.schedule_case.assert_not_called()
