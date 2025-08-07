import pytest
from unittest.mock import MagicMock, patch

from src.controllers.application import Application
from src.controllers.interfaces import ILifecycleManager
from src.domain.interfaces import IWorkflowOrchestrator

class TestApplication:
    @pytest.fixture
    def mock_lm(self) -> MagicMock:
        return MagicMock(spec=ILifecycleManager)

    @pytest.fixture
    def mock_orchestrator(self) -> MagicMock:
        return MagicMock(spec=IWorkflowOrchestrator)

    @pytest.fixture
    def app(self, mock_lm, mock_orchestrator) -> Application:
        return Application(
            lifecycle_manager=mock_lm,
            orchestrator=mock_orchestrator,
            scan_interval=1 # Use a short interval for testing
        )

    @patch('time.sleep')
    def test_start_and_shutdown(self, mock_sleep, app, mock_lm, mock_orchestrator):
        # Given
        mock_lm.acquire_lock.return_value = True

        # This is a bit tricky to test the loop. We'll have the orchestrator
        # stop the app after the first iteration by calling shutdown.
        def stop_app_on_process():
            app.shutdown()
        mock_orchestrator.process_new_cases.side_effect = stop_app_on_process

        # When
        app.start()

        # Then
        mock_lm.acquire_lock.assert_called_once()
        mock_lm.register_shutdown_handler.assert_called_once_with(app.shutdown)
        mock_orchestrator.process_new_cases.assert_called_once()
        mock_lm.release_lock.assert_called_once()

    def test_start_fails_if_lock_not_acquired(self, app, mock_lm):
        # Given
        mock_lm.acquire_lock.return_value = False

        # When
        app.start()

        # Then
        mock_lm.acquire_lock.assert_called_once()
        mock_lm.register_shutdown_handler.assert_not_called()

    def test_shutdown_is_idempotent(self, app, mock_lm):
        # Given
        app._running = False # Pretend it's not running

        # When
        app.shutdown()

        # Then
        mock_lm.release_lock.assert_not_called()
