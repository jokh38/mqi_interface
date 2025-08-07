import pytest
from unittest.mock import MagicMock
from collections import deque
from typing import Optional, Deque

from src.domain.models import Task, TaskType, Case, Job
from src.services.interfaces import ICaseService, IJobService

from src.domain.task_scheduler import TaskScheduler

class TestTaskScheduler:
    @pytest.fixture
    def mock_case_service(self) -> MagicMock:
        return MagicMock(spec=ICaseService)

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        return MagicMock(spec=IJobService)

    @pytest.fixture
    def scheduler(self, mock_case_service, mock_job_service) -> TaskScheduler:
        return TaskScheduler(case_service=mock_case_service, job_service=mock_job_service)

    def test_schedule_case_creates_tasks(self, scheduler, mock_case_service, mock_job_service):
        # Given
        case = Case(case_id="case001")
        job = Job(job_id="job001", case_id="case001")
        mock_case_service.get_case.return_value = case
        mock_job_service.create_job.return_value = job

        # When
        scheduler.schedule_case("case001")

        # Then
        assert len(scheduler._task_queue) == 5
        # Check that the first task is the upload task
        assert scheduler._task_queue[0].type == TaskType.UPLOAD
        assert scheduler._task_queue[0].job_id == "job001"

    def test_get_next_task(self, scheduler, mock_case_service, mock_job_service):
        # Given
        self.test_schedule_case_creates_tasks(scheduler, mock_case_service, mock_job_service)

        # When
        task1 = scheduler.get_next_task()
        task2 = scheduler.get_next_task()

        # Then
        assert task1 is not None
        assert task1.type == TaskType.UPLOAD
        assert task2 is not None
        assert task2.type == TaskType.INTERPRET
        assert len(scheduler._task_queue) == 3

    def test_get_next_task_from_empty_queue(self, scheduler):
        # When
        task = scheduler.get_next_task()

        # Then
        assert task is None
