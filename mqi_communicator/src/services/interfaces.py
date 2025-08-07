from typing import Protocol, List, Optional

from ..domain.models import Case

class IFileSystem(Protocol):
    """An interface for file system operations."""
    def list_directories(self, path: str) -> List[str]:
        ...

from ..domain.models import Job

class ITransferService(Protocol):
    """An interface for a service that manages file transfers."""
    def upload_case(self, case_id: str) -> None:
        ...

    def download_results(self, case_id: str) -> None:
        ...

class IJobService(Protocol):
    """An interface for a service that manages jobs."""
    def create_job(self, case_id: str) -> Job:
        ...

    def allocate_resources_for_job(self, job: Job) -> bool:
        ...

    def complete_job(self, job_id: str) -> None:
        ...

class ICaseService(Protocol):
    """An interface for a service that manages cases."""
    def scan_for_new_cases(self) -> List[str]:
        ...

    def get_case(self, case_id: str) -> Optional[Case]:
        ...

    def update_case_status(self, case_id: str, status: str) -> None:
        ...

class IResourceService(Protocol):
    """
    An interface for a service that manages system resources, such as GPUs.
    """

    def allocate_gpus(self, count: int) -> Optional[List[int]]:
        """
        Allocates a specified number of GPUs.

        Args:
            count (int): The number of GPUs to allocate.

        Returns:
            A list of GPU IDs if the allocation is successful, otherwise None.
        """
        ...

    def release_gpus(self, gpu_ids: List[int]) -> None:
        """
        Releases a list of GPUs back to the available pool.

        Args:
            gpu_ids (List[int]): The list of GPU IDs to release.
        """
        ...

    def get_available_gpu_count(self) -> int:
        """
        Returns the number of currently available GPUs.
        """
        ...
