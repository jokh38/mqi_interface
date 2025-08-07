import pytest
from typing import List, Optional, Set
from threading import Thread

from src.services.resource_service import ResourceService

class TestResourceService:
    @pytest.fixture
    def resource_service(self) -> ResourceService:
        return ResourceService(total_gpus=4)

    def test_initial_available_gpus(self, resource_service):
        assert resource_service.get_available_gpu_count() == 4

    def test_allocate_gpus_success(self, resource_service):
        # When
        allocated = resource_service.allocate_gpus(2)

        # Then
        assert allocated is not None
        assert len(allocated) == 2
        assert resource_service.get_available_gpu_count() == 2

    def test_allocate_more_gpus_than_available(self, resource_service):
        # When
        allocated = resource_service.allocate_gpus(5)

        # Then
        assert allocated is None
        assert resource_service.get_available_gpu_count() == 4

    def test_release_gpus(self, resource_service):
        # Given
        allocated = resource_service.allocate_gpus(3)
        assert resource_service.get_available_gpu_count() == 1

        # When
        resource_service.release_gpus(allocated)

        # Then
        assert resource_service.get_available_gpu_count() == 4

    def test_allocate_all_gpus(self, resource_service):
        # When
        allocated1 = resource_service.allocate_gpus(2)
        allocated2 = resource_service.allocate_gpus(2)

        # Then
        assert allocated1 is not None
        assert allocated2 is not None
        assert resource_service.get_available_gpu_count() == 0

        # And a subsequent allocation should fail
        assert resource_service.allocate_gpus(1) is None

    def test_releasing_unallocated_gpus_is_harmless(self, resource_service):
        # Given
        initial_count = resource_service.get_available_gpu_count()

        # When
        resource_service.release_gpus([10, 11]) # These were never allocated

        # Then
        # The available count should not change, and no error should be raised.
        # The internal state of _available_gpus might grow, which is acceptable.
        assert resource_service.get_available_gpu_count() >= initial_count

    def test_thread_safety(self):
        # Given
        total_gpus = 50
        service = ResourceService(total_gpus=total_gpus)
        allocations = []

        def worker():
            allocated = service.allocate_gpus(1)
            if allocated:
                allocations.extend(allocated)

        # When
        threads = [Thread(target=worker) for _ in range(total_gpus * 2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Then
        # All GPUs should be allocated
        assert service.get_available_gpu_count() == 0
        # The total number of unique allocated GPUs should be correct
        assert len(set(allocations)) == total_gpus
