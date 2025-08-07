from typing import Protocol, Tuple

import subprocess
from typing import Tuple, Protocol

class IExecutor(Protocol):
    """An interface for command executors."""

    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Executes a command and returns the result.

        Args:
            command (str): The command to execute.

        Returns:
            A tuple containing the exit code (int), stdout (str), and stderr (str).
        """
        ...

from .connection import SSHConnectionPool

class RemoteExecutor(IExecutor):
    """
    An executor that runs commands on a remote machine over SSH.

    This executor uses a connection pool to manage SSH connections.
    """
    def __init__(self, connection_pool: SSHConnectionPool):
        self.pool = connection_pool

    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Executes a shell command on the remote host.

        Args:
            command (str): The command to execute.

        Returns:
            A tuple containing the command's exit code, stdout, and stderr.
        """
        with self.pool.connection_context() as conn:
            _, stdout, stderr = conn.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            return exit_code, stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

class LocalExecutor(IExecutor):
    """
    An executor that runs commands on the local machine using subprocess.
    """
    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Executes a shell command on the local host.

        Args:
            command (str): The command to execute.

        Returns:
            A tuple containing the command's exit code, stdout, and stderr.
        """
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
