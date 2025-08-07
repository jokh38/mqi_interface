import pytest
import subprocess
from typing import Tuple

from src.infrastructure.executors import LocalExecutor, RemoteExecutor
from unittest.mock import MagicMock

class TestRemoteExecutor:
    @pytest.fixture
    def mock_pool(self):
        return MagicMock()

    @pytest.fixture
    def mock_ssh_connection(self):
        conn = MagicMock()
        stdout_mock = MagicMock()
        stdout_mock.channel.recv_exit_status.return_value = 0
        stdout_mock.read.return_value = b"remote output"

        stderr_mock = MagicMock()
        stderr_mock.read.return_value = b"remote error"

        conn.exec_command.return_value = (MagicMock(), stdout_mock, stderr_mock)
        return conn

    def test_execute_success(self, mock_pool, mock_ssh_connection):
        # Given
        mock_pool.connection_context.return_value.__enter__.return_value = mock_ssh_connection
        executor = RemoteExecutor(mock_pool)
        command = "ls -l"

        # When
        return_code, stdout, stderr = executor.execute(command)

        # Then
        assert return_code == 0
        assert stdout == "remote output"
        assert stderr == "remote error"
        mock_pool.connection_context.assert_called_once()
        mock_ssh_connection.exec_command.assert_called_once_with(command)

class TestLocalExecutor:
    def test_execute_success(self):
        # Given
        executor = LocalExecutor()
        command = "echo 'hello world'"

        # When
        return_code, stdout, stderr = executor.execute(command)

        # Then
        assert return_code == 0
        assert stdout.strip() == "hello world"
        assert stderr == ""

    def test_execute_failure(self):
        # Given
        executor = LocalExecutor()
        # Use a command that is guaranteed to fail and produce stderr
        command = "ls /non_existent_directory_12345"

        # When
        return_code, stdout, stderr = executor.execute(command)

        # Then
        assert return_code != 0
        assert stdout == ""
        assert "No such file or directory" in stderr

    def test_execute_with_complex_command(self):
        # Given
        executor = LocalExecutor()
        command = "echo 'line1' && echo 'line2' >&2"

        # When
        return_code, stdout, stderr = executor.execute(command)

        # Then
        assert return_code == 0
        assert stdout.strip() == "line1"
        assert stderr.strip() == "line2"
