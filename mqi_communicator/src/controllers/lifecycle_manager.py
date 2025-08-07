import os
import signal
import logging
from pathlib import Path
from typing import Callable

from .interfaces import ILifecycleManager

logger = logging.getLogger(__name__)

class LifecycleManager(ILifecycleManager):
    """
    Manages the application's lifecycle, including PID file locking and
    graceful shutdown signal handling.

    Args:
        pid_file (Path): The path to the PID file to use for locking.
    """
    def __init__(self, pid_file: Path):
        self._pid_file = pid_file
        self._pid_fd = None

    def acquire_lock(self) -> bool:
        """
        Acquires a process lock using a PID file.

        This ensures that only one instance of the application can run at a time.

        Returns:
            True if the lock was acquired, False otherwise.
        """
        if self._pid_file.exists():
            try:
                with open(self._pid_file, 'r') as f:
                    pid = int(f.read().strip())
                # Check if the process is actually running
                os.kill(pid, 0)
                logger.warning(f"Application is already running with PID {pid}.")
                return False
            except (IOError, OSError, ValueError):
                # The PID file is stale, so we can overwrite it.
                logger.warning("Stale PID file found. Overwriting.")
                self._pid_file.unlink()

        try:
            self._pid_fd = os.open(self._pid_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(self._pid_fd, str(os.getpid()).encode())
            logger.info(f"Acquired process lock with PID {os.getpid()}.")
            return True
        except (IOError, OSError):
            logger.exception("Failed to acquire process lock.")
            return False

    def release_lock(self) -> None:
        """
        Releases the process lock by closing and deleting the PID file.
        """
        if self._pid_fd:
            os.close(self._pid_fd)
            self._pid_file.unlink()
            logger.info("Process lock released.")

    def register_shutdown_handler(self, handler: Callable[..., None]) -> None:
        """
        Registers a handler to be called on SIGINT or SIGTERM.

        Args:
            handler: The function to call upon receiving a shutdown signal.
        """
        def signal_handler(signum, frame):
            logger.info(f"Received shutdown signal: {signal.Signals(signum).name}")
            handler()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logger.info("Registered shutdown handlers.")
