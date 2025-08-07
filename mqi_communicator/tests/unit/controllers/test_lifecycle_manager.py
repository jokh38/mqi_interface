import pytest
from unittest.mock import MagicMock, mock_open, patch
import os
import signal
from pathlib import Path

from src.controllers.lifecycle_manager import LifecycleManager

class TestLifecycleManager:
    @pytest.fixture
    def pid_file(self) -> Path:
        return Path("/tmp/test_app.pid")

    @patch('os.open')
    @patch('os.write')
    @patch('os.getpid', return_value=12345)
    def test_acquire_lock_success(self, mock_getpid, mock_write, mock_open, pid_file):
        # Given
        lm = LifecycleManager(pid_file)

        # When
        result = lm.acquire_lock()

        # Then
        assert result is True
        mock_open.assert_called_once_with(pid_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        mock_write.assert_called_once()

    @patch('os.open', side_effect=IOError)
    def test_acquire_lock_failure(self, mock_open, pid_file):
        # Given
        lm = LifecycleManager(pid_file)

        # When
        result = lm.acquire_lock()

        # Then
        assert result is False

    @patch('os.close')
    @patch('pathlib.Path.unlink')
    def test_release_lock(self, mock_unlink, mock_close, pid_file):
        # Given
        lm = LifecycleManager(pid_file)
        lm._pid_fd = 5 # Dummy file descriptor

        # When
        lm.release_lock()

        # Then
        mock_close.assert_called_once_with(5)
        mock_unlink.assert_called_once()

    @patch('os.open')
    @patch('os.write')
    @patch('os.getpid', return_value=12345)
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="54321")
    @patch('os.kill', side_effect=OSError) # Simulate process not running
    @patch('pathlib.Path.unlink')
    def test_acquire_lock_with_stale_pid_file(self, mock_unlink, mock_kill, mock_read_open, mock_path_exists, mock_getpid, mock_write, mock_os_open, pid_file):
        # Given
        lm = LifecycleManager(pid_file)

        # When
        result = lm.acquire_lock()

        # Then
        assert result is True
        mock_unlink.assert_called_once()
        mock_os_open.assert_called_once()

    @patch('signal.signal')
    def test_register_shutdown_handler(self, mock_signal, pid_file):
        # Given
        lm = LifecycleManager(pid_file)
        mock_handler = MagicMock()

        # When
        lm.register_shutdown_handler(mock_handler)

        # Then
        from unittest.mock import ANY
        # Verify that signal.signal was called for SIGINT and SIGTERM
        mock_signal.assert_any_call(signal.SIGINT, ANY)
        mock_signal.assert_any_call(signal.SIGTERM, ANY)

        # Find the actual handler function that was registered
        sigint_handler = None
        for call in mock_signal.call_args_list:
            if call.args[0] == signal.SIGINT:
                sigint_handler = call.args[1]
                break

        assert sigint_handler is not None

        # Call the registered handler and verify our mock was called
        sigint_handler(signal.SIGINT, None)
        mock_handler.assert_called_once()
