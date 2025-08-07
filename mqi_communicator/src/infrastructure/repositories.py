from typing import List, Optional, Dict, Any
from dataclasses import asdict

from datetime import datetime
from ..domain.models import Case, Job, CaseStatus, JobStatus
from ..domain.repositories import ICaseRepository, IJobRepository
from .state import StateManager

class CaseRepository(ICaseRepository):
    """
    A repository for managing Case objects using a StateManager for persistence.
    """
    def __init__(self, state_manager: StateManager):
        self._sm = state_manager

    def add(self, case: Case) -> None:
        """Adds a new case to the repository."""
        with self._sm.transaction():
            self._sm.set(f"cases.{case.case_id}", asdict(case))

    def get(self, case_id: str) -> Optional[Case]:
        """Gets a case by its ID."""
        case_data = self._sm.get(f"cases.{case_id}")
        if case_data:
            # Convert string representations back to proper types
            case_data["status"] = CaseStatus(case_data["status"])
            case_data["created_at"] = datetime.fromisoformat(case_data["created_at"])
            case_data["updated_at"] = datetime.fromisoformat(case_data["updated_at"])
            return Case(**case_data)
        return None

    def list_all(self) -> List[Case]:
        """Lists all cases in the repository."""
        all_cases_data = self._sm.get("cases", {})
        cases = []
        for data in all_cases_data.values():
            data["status"] = CaseStatus(data["status"])
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            cases.append(Case(**data))
        return cases

    def update(self, case: Case) -> None:
        """Updates an existing case. For this implementation, it's the same as add."""
        self.add(case)


class JobRepository(IJobRepository):
    """
    A repository for managing Job objects using a StateManager for persistence.
    """
    def __init__(self, state_manager: StateManager):
        self._sm = state_manager

    def add(self, job: Job) -> None:
        """Adds a new job to the repository."""
        with self._sm.transaction():
            self._sm.set(f"jobs.{job.job_id}", asdict(job))

    def get(self, job_id: str) -> Optional[Job]:
        """Gets a job by its ID."""
        job_data = self._sm.get(f"jobs.{job_id}")
        if job_data:
            job_data["status"] = JobStatus(job_data["status"])
            job_data["created_at"] = datetime.fromisoformat(job_data["created_at"])
            if job_data.get("started_at"):
                job_data["started_at"] = datetime.fromisoformat(job_data["started_at"])
            if job_data.get("completed_at"):
                job_data["completed_at"] = datetime.fromisoformat(job_data["completed_at"])
            return Job(**job_data)
        return None

    def list_all(self) -> List[Job]:
        """Lists all jobs in the repository."""
        all_jobs_data = self._sm.get("jobs", {})
        jobs = []
        for data in all_jobs_data.values():
            data["status"] = JobStatus(data["status"])
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            if data.get("started_at"):
                data["started_at"] = datetime.fromisoformat(data["started_at"])
            if data.get("completed_at"):
                data["completed_at"] = datetime.fromisoformat(data["completed_at"])
            jobs.append(Job(**data))
        return jobs

    def update(self, job: Job) -> None:
        """Updates an existing job."""
        self.add(job)
