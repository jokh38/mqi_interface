from typing import Protocol, List, Optional
from .models import Case, Job

class ICaseRepository(Protocol):
    """Interface for a repository that manages Case objects."""

    def add(self, case: Case) -> None:
        """Adds a new case to the repository."""
        ...

    def get(self, case_id: str) -> Optional[Case]:
        """Gets a case by its ID."""
        ...

    def list_all(self) -> List[Case]:
        """Lists all cases in the repository."""
        ...

    def update(self, case: Case) -> None:
        """Updates an existing case."""
        ...

class IJobRepository(Protocol):
    """Interface for a repository that manages Job objects."""

    def add(self, job: Job) -> None:
        """Adds a new job to the repository."""
        ...

    def get(self, job_id: str) -> Optional[Job]:
        """Gets a job by its ID."""
        ...

    def list_all(self) -> List[Job]:
        """Lists all jobs in the repository."""
        ...

    def update(self, job: Job) -> None:
        """Updates an existing job."""
        ...
