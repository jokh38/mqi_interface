from typing import List, Optional

from ..domain.models import Case, CaseStatus
from ..domain.repositories import ICaseRepository
from .interfaces import IFileSystem, ICaseService

class CaseService(ICaseService):
    """
    A service for managing the lifecycle of cases.

    This service is responsible for finding new cases from the file system,
    adding them to the repository, and updating their status.

    Args:
        case_repository (ICaseRepository): The repository for case data.
        file_system (IFileSystem): The file system to scan for new cases.
        scan_path (str): The path to scan for new case directories.
    """
    def __init__(
        self,
        case_repository: ICaseRepository,
        file_system: IFileSystem,
        scan_path: str
    ):
        self._repo = case_repository
        self._fs = file_system
        self._scan_path = scan_path

    def scan_for_new_cases(self) -> List[str]:
        """
        Scans the file system for new cases and adds them to the repository.

        Returns:
            A list of case IDs for the newly found cases.
        """
        try:
            fs_cases = set(self._fs.list_directories(self._scan_path))
        except FileNotFoundError:
            # If the scan path doesn't exist, there are no new cases.
            return []

        repo_cases = {case.case_id for case in self._repo.list_all()}

        new_case_ids = list(fs_cases - repo_cases)

        for case_id in new_case_ids:
            new_case = Case(case_id=case_id)
            self._repo.add(new_case)

        return new_case_ids

    def get_case(self, case_id: str) -> Optional[Case]:
        """
        Retrieves a case by its ID.

        Args:
            case_id (str): The ID of the case to retrieve.

        Returns:
            The Case object if found, otherwise None.
        """
        return self._repo.get(case_id)

    def update_case_status(self, case_id: str, status: CaseStatus) -> None:
        """
        Updates the status of a specific case.

        Args:
            case_id (str): The ID of the case to update.
            status (CaseStatus): The new status for the case.
        """
        case = self._repo.get(case_id)
        if case:
            case.status = status
            self._repo.update(case)
