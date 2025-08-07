import uuid
from typing import Optional

from ..domain.models import Job, JobStatus
from ..domain.repositories import IJobRepository
from .interfaces import IResourceService, IJobService

class JobService(IJobService):
    """
    A service for managing the lifecycle of jobs.

    This service handles job creation, resource allocation, and completion.

    Args:
        job_repository (IJobRepository): The repository for job data.
        resource_service (IResourceService): The service for managing resources.
    """
    def __init__(self, job_repository: IJobRepository, resource_service: IResourceService):
        self._repo = job_repository
        self._resource_service = resource_service

    def create_job(self, case_id: str) -> Job:
        """
        Creates a new job for a given case.

        Args:
            case_id (str): The ID of the case to associate the job with.

        Returns:
            The newly created Job object.
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, case_id=case_id)
        self._repo.add(job)
        return job

    def allocate_resources_for_job(self, job: Job, gpus_required: int = 1) -> bool:
        """
        Attempts to allocate resources for a given job.

        Args:
            job (Job): The job that requires resources.
            gpus_required (int): The number of GPUs required for the job.

        Returns:
            True if resources were successfully allocated, False otherwise.
        """
        gpu_ids = self._resource_service.allocate_gpus(gpus_required)
        if gpu_ids:
            job.gpu_allocation = gpu_ids
            job.status = JobStatus.RUNNING
            self._repo.update(job)
            return True
        return False

    def complete_job(self, job_id: str) -> None:
        """
        Marks a job as complete and releases its resources.

        Args:
            job_id (str): The ID of the job to complete.
        """
        job = self._repo.get(job_id)
        if job:
            if job.gpu_allocation:
                self._resource_service.release_gpus(job.gpu_allocation)
            job.status = JobStatus.COMPLETED
            self._repo.update(job)
