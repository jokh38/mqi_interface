import time
import logging

from .interfaces import IApplication, ILifecycleManager
from ..domain.interfaces import IWorkflowOrchestrator

logger = logging.getLogger(__name__)

class Application(IApplication):
    """
    The main application class.

    This class orchestrates the entire application lifecycle, including
    startup, the main processing loop, and shutdown.

    Args:
        lifecycle_manager (ILifecycleManager): The manager for process lifecycle.
        orchestrator (IWorkflowOrchestrator): The main workflow orchestrator.
        scan_interval (int): The interval in seconds between scans for new cases.
    """
    def __init__(
        self,
        lifecycle_manager: ILifecycleManager,
        orchestrator: IWorkflowOrchestrator,
        scan_interval: int = 60,
    ):
        self._lm = lifecycle_manager
        self._orchestrator = orchestrator
        self._scan_interval = scan_interval
        self._running = False

    def start(self) -> None:
        """
        Starts the main application loop.
        """
        if not self._lm.acquire_lock():
            logger.error("Application is already running. Exiting.")
            return

        self._lm.register_shutdown_handler(self.shutdown)
        self._running = True
        logger.info("Application started.")

        while self._running:
            try:
                self._orchestrator.process_new_cases()
                logger.info(f"Main loop iteration complete. Waiting {self._scan_interval} seconds.")
                time.sleep(self._scan_interval)
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {e}", exc_info=True)
                # In a real-world scenario, you might want more sophisticated error handling here,
                # like a circuit breaker for the main loop or a limited number of retries.
                time.sleep(self._scan_interval)

    def shutdown(self) -> None:
        """
        Performs a graceful shutdown of the application.
        """
        if not self._running:
            return

        logger.info("Shutting down application...")
        self._running = False
        self._lm.release_lock()
        logger.info("Application shutdown complete.")
