import pytest
from datetime import datetime
from src.domain.models import Case, Job, Task, CaseStatus, JobStatus, TaskType

class TestDomainModels:
    def test_case_creation(self):
        # Given
        case_id = "case_001"

        # When
        case = Case(case_id=case_id, beam_count=10)

        # Then
        assert case.case_id == case_id
        assert case.beam_count == 10
        assert case.status == CaseStatus.NEW
        assert isinstance(case.created_at, datetime)
        assert isinstance(case.updated_at, datetime)
        assert case.metadata == {}

    def test_job_creation(self):
        # Given
        job_id = "job_001"
        case_id = "case_001"

        # When
        job = Job(job_id=job_id, case_id=case_id, priority=5)

        # Then
        assert job.job_id == job_id
        assert job.case_id == case_id
        assert job.priority == 5
        assert job.status == JobStatus.PENDING
        assert job.gpu_allocation == []
        assert job.started_at is None
        assert job.completed_at is None

    def test_task_creation(self):
        # Given
        task_id = "task_001"
        job_id = "job_001"

        # When
        task = Task(task_id=task_id, job_id=job_id, type=TaskType.UPLOAD)

        # Then
        assert task.task_id == task_id
        assert task.job_id == job_id
        assert task.type == TaskType.UPLOAD
        assert task.parameters == {}
        assert task.status == "pending"

    def test_enum_values(self):
        # Just to be sure the string values are correct
        assert CaseStatus.COMPLETED.value == "completed"
        assert JobStatus.RUNNING.value == "running"
        assert TaskType.BEAM_CALC.value == "beam_calc"
