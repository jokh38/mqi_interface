from collections import deque
from typing import Deque, Optional

from .models import Task, TaskType, Case, Job
from ..services.interfaces import ICaseService, IJobService
from .interfaces import ITaskScheduler

class TaskScheduler(ITaskScheduler):
    """
    A simple, in-memory task scheduler that creates a fixed sequence of tasks for a case.

    This scheduler is responsible for generating the tasks required to process
    a case and providing them in the correct order.

    Args:
        case_service (ICaseService): The service for retrieving case information.
        job_service (IJobService): The service for creating jobs.
    """
    def __init__(self, case_service: ICaseService, job_service: IJobService):
        self._case_service = case_service
        self._job_service = job_service
        self._task_queue: Deque[Task] = deque()

    def schedule_case(self, case_id: str) -> None:
        """
        Schedules all the necessary tasks for a given case.

        This creates a new job for the case and populates the task queue
        with the standard sequence of tasks.

        Args:
            case_id (str): The ID of the case to schedule.
        """
        case = self._case_service.get_case(case_id)
        if not case:
            # Handle case not found, maybe log an error
            return

        job = self._job_service.create_job(case.case_id)

        # Create a fixed sequence of tasks for the job
        tasks = [
            Task(task_id=f"{job.job_id}_upload", job_id=job.job_id, type=TaskType.UPLOAD),
            Task(task_id=f"{job.job_id}_interpret", job_id=job.job_id, type=TaskType.INTERPRET),
            Task(task_id=f"{job.job_id}_beam_calc", job_id=job.job_id, type=TaskType.BEAM_CALC),
            Task(task_id=f"{job.job_id}_convert", job_id=job.job_id, type=TaskType.CONVERT),
            Task(task_id=f"{job.job_id}_download", job_id=job.job_id, type=TaskType.DOWNLOAD),
        ]
        self._task_queue.extend(tasks)

    def get_next_task(self) -> Optional[Task]:
        """
        Gets the next task to be executed from the queue.

        Returns:
            The next Task object if the queue is not empty, otherwise None.
        """
        if not self._task_queue:
            return None
        return self._task_queue.popleft()

    def complete_task(self, task_id: str) -> None:
        """
        Marks a task as complete.

        Note: In this simple implementation, this method does nothing. A more
        complex scheduler might update a task repository or trigger dependent tasks.

        Args:
            task_id (str): The ID of the task to mark as complete.
        """
        # In a more advanced implementation, we might have a task repository
        # and update the task's status here.
        pass
