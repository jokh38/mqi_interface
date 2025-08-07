from typing import List, Optional, Set
import threading

from .interfaces import IResourceService

class ResourceService(IResourceService):
    """
    A service for managing and allocating GPU resources in a thread-safe manner.

    This service keeps track of a finite set of GPUs, allowing them to be
    allocated for processing jobs and released when jobs are complete.

    Args:
        total_gpus (int): The total number of GPUs available for allocation.
    """
    def __init__(self, total_gpus: int):
        self._available_gpus: Set[int] = set(range(total_gpus))
        self._lock = threading.Lock()

    def allocate_gpus(self, count: int) -> Optional[List[int]]:
        """
        Allocates a specified number of GPUs atomically.

        Args:
            count (int): The number of GPUs to allocate.

        Returns:
            A list of GPU IDs if the allocation is successful, otherwise None.
        """
        with self._lock:
            if count > len(self._available_gpus):
                return None

            # This is a simple way to get 'count' items from a set without ordering
            allocated = [self._available_gpus.pop() for _ in range(count)]
            return allocated

    def release_gpus(self, gpu_ids: List[int]) -> None:
        """
        Releases a list of GPUs back to the available pool atomically.

        Args:
            gpu_ids (List[int]): The list of GPU IDs to release.
        """
        with self._lock:
            self._available_gpus.update(gpu_ids)

    def get_available_gpu_count(self) -> int:
        """
        Returns the number of currently available GPUs.
        """
        with self._lock:
            return len(self._available_gpus)
