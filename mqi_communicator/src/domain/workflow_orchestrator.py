from ..services.interfaces import ICaseService
from .interfaces import ITaskScheduler, IWorkflowOrchestrator
import logging

logger = logging.getLogger(__name__)

class WorkflowOrchestrator(IWorkflowOrchestrator):
    """
    The main orchestrator for the application's workflow.

    This class coordinates the high-level process of scanning for new cases
    and scheduling them for processing.

    Args:
        case_service (ICaseService): The service for finding new cases.
        task_scheduler (ITaskScheduler): The scheduler for queueing up tasks.
    """
    def __init__(self, case_service: ICaseService, task_scheduler: ITaskScheduler):
        self._case_service = case_service
        self._task_scheduler = task_scheduler

    def process_new_cases(self) -> None:
        """
        Scans for new cases and schedules them for processing.
        """
        logger.info("Starting scan for new cases...")
        try:
            new_case_ids = self._case_service.scan_for_new_cases()
            if not new_case_ids:
                logger.info("No new cases found.")
                return

            logger.info(f"Found {len(new_case_ids)} new cases: {new_case_ids}")
            for case_id in new_case_ids:
                logger.info(f"Scheduling tasks for case: {case_id}")
                self._task_scheduler.schedule_case(case_id)

            logger.info("Finished scheduling new cases.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during case processing: {e}", exc_info=True)
