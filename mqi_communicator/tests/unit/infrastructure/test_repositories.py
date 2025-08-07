import pytest
from unittest.mock import MagicMock
from typing import Dict, Any, Optional, List

from src.domain.models import Case, Job, CaseStatus, JobStatus
from src.infrastructure.repositories import CaseRepository, JobRepository


class TestJobRepository:
    @pytest.fixture
    def mock_state_manager(self):
        # A simple in-memory mock for the state manager
        mock = MagicMock()
        state: Dict[str, Any] = {}

        def get_side_effect(key, default=None):
            keys = key.split('.')
            value = state
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            return value if value is not None else default

        def set_side_effect(key, value):
            keys = key.split('.')
            current = state
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value

        mock.get.side_effect = get_side_effect
        mock.set.side_effect = set_side_effect
        mock.transaction.return_value.__enter__.return_value = None

        return mock

    @pytest.fixture
    def sample_job(self) -> Job:
        return Job(job_id="job001", case_id="case001", status=JobStatus.PENDING)

    def test_add_and_get_job(self, mock_state_manager, sample_job):
        # Given
        repo = JobRepository(mock_state_manager)

        # When
        repo.add(sample_job)
        retrieved_job = repo.get(sample_job.job_id)

        # Then
        assert retrieved_job is not None
        assert retrieved_job.job_id == sample_job.job_id
        assert retrieved_job.status == sample_job.status

class TestCareRepository:
    @pytest.fixture
    def mock_state_manager(self):
        # A simple in-memory mock for the state manager
        mock = MagicMock()
        state: Dict[str, Any] = {}

        def get_side_effect(key, default=None):
            keys = key.split('.')
            value = state
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            return value if value is not None else default

        def set_side_effect(key, value):
            keys = key.split('.')
            current = state
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value

        mock.get.side_effect = get_side_effect
        mock.set.side_effect = set_side_effect
        mock.transaction.return_value.__enter__.return_value = None

        return mock

    @pytest.fixture
    def sample_case(self) -> Case:
        return Case(case_id="case001", status=CaseStatus.NEW)

    def test_add_and_get_case(self, mock_state_manager, sample_case):
        # Given
        repo = CaseRepository(mock_state_manager)

        # When
        repo.add(sample_case)
        retrieved_case = repo.get(sample_case.case_id)

        # Then
        assert retrieved_case is not None
        assert retrieved_case.case_id == sample_case.case_id
        assert retrieved_case.status == sample_case.status

    def test_get_nonexistent_case(self, mock_state_manager):
        # Given
        repo = CaseRepository(mock_state_manager)

        # When
        retrieved_case = repo.get("nonexistent_id")

        # Then
        assert retrieved_case is None

    def test_list_all_cases(self, mock_state_manager, sample_case):
        # Given
        repo = CaseRepository(mock_state_manager)
        case2 = Case(case_id="case002")
        repo.add(sample_case)
        repo.add(case2)

        # When
        all_cases = repo.list_all()

        # Then
        assert len(all_cases) == 2
        assert {c.case_id for c in all_cases} == {"case001", "case002"}

    def test_update_case(self, mock_state_manager, sample_case):
        # Given
        repo = CaseRepository(mock_state_manager)
        repo.add(sample_case)

        # When
        sample_case.status = CaseStatus.PROCESSING
        repo.update(sample_case)
        retrieved_case = repo.get(sample_case.case_id)

        # Then
        assert retrieved_case is not None
        assert retrieved_case.status == CaseStatus.PROCESSING
