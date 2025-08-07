import pytest
from unittest.mock import MagicMock

from src.services.resource_service import ResourceService
from src.services.job_service import JobService
from src.domain.models import Job
from src.domain.repositories import IJobRepository

class TestServiceIntegration:
    def test_job_service_allocates_from_resource_service(self):
        # Given
        # We use a real ResourceService
        resource_service = ResourceService(total_gpus=4)

        # We mock the repository layer, as we're testing service interaction
        mock_repo = MagicMock(spec=IJobRepository)

        # We use a real JobService
        job_service = JobService(
            job_repository=mock_repo,
            resource_service=resource_service
        )

        job = Job(job_id="job001", case_id="case001")

        # When
        # We ask the job service to allocate resources for the job
        success = job_service.allocate_resources_for_job(job, gpus_required=2)

        # Then
        assert success is True
        # Verify that the resource service has fewer GPUs available
        assert resource_service.get_available_gpu_count() == 2
        # Verify that the job object was updated correctly
        assert len(job.gpu_allocation) == 2
        # Verify that the repository was called to save the updated job
        mock_repo.update.assert_called_once_with(job)
