import pytest
from unittest.mock import MagicMock
import uuid

from src.domain.models import Job, JobStatus
from src.domain.repositories import IJobRepository
from src.services.interfaces import IResourceService

from src.services.job_service import JobService

class TestJobService:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        return MagicMock(spec=IJobRepository)

    @pytest.fixture
    def mock_resource_service(self) -> MagicMock:
        return MagicMock(spec=IResourceService)

    @pytest.fixture
    def job_service(self, mock_repo, mock_resource_service) -> JobService:
        return JobService(job_repository=mock_repo, resource_service=mock_resource_service)

    def test_create_job(self, job_service, mock_repo):
        # Given
        case_id = "case001"

        # When
        job = job_service.create_job(case_id)

        # Then
        assert job.case_id == case_id
        assert job.status == JobStatus.PENDING
        mock_repo.add.assert_called_once_with(job)

    def test_allocate_resources_success(self, job_service, mock_resource_service, mock_repo):
        # Given
        job = Job(job_id="job001", case_id="case001")
        mock_resource_service.allocate_gpus.return_value = [1] # Success

        # When
        result = job_service.allocate_resources_for_job(job)

        # Then
        assert result is True
        assert job.gpu_allocation == [1]
        assert job.status == JobStatus.RUNNING
        mock_repo.update.assert_called_once_with(job)

    def test_allocate_resources_failure(self, job_service, mock_resource_service, mock_repo):
        # Given
        job = Job(job_id="job001", case_id="case001")
        mock_resource_service.allocate_gpus.return_value = None # Failure

        # When
        result = job_service.allocate_resources_for_job(job)

        # Then
        assert result is False
        assert job.gpu_allocation == []
        assert job.status == JobStatus.PENDING # Status should not change
        mock_repo.update.assert_not_called()

    def test_complete_job(self, job_service, mock_resource_service, mock_repo):
        # Given
        job = Job(job_id="job001", case_id="case001", gpu_allocation=[1])
        mock_repo.get.return_value = job

        # When
        job_service.complete_job("job001")

        # Then
        mock_resource_service.release_gpus.assert_called_once_with([1])
        assert job.status == JobStatus.COMPLETED
        mock_repo.update.assert_called_once_with(job)
