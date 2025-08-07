import pytest
from unittest.mock import MagicMock
from typing import List, Optional

from src.domain.models import Case, CaseStatus
from src.domain.repositories import ICaseRepository
from src.services.interfaces import IFileSystem

from src.services.case_service import CaseService

class TestCareService:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        return MagicMock(spec=ICaseRepository)

    @pytest.fixture
    def mock_fs(self) -> MagicMock:
        return MagicMock(spec=IFileSystem)

    @pytest.fixture
    def case_service(self, mock_repo, mock_fs) -> CaseService:
        return CaseService(
            case_repository=mock_repo,
            file_system=mock_fs,
            scan_path="/data/new_cases"
        )

    def test_scan_finds_new_cases(self, case_service, mock_repo, mock_fs):
        # Given
        mock_fs.list_directories.return_value = ["case1", "case2", "case3"]
        mock_repo.list_all.return_value = [Case(case_id="case1")]

        # When
        new_cases = case_service.scan_for_new_cases()

        # Then
        assert set(new_cases) == {"case2", "case3"}
        # Check that add was called for each new case
        assert mock_repo.add.call_count == 2
        # Verify the case_ids of the added cases
        added_cases = {call.args[0].case_id for call in mock_repo.add.call_args_list}
        assert added_cases == {"case2", "case3"}

    def test_scan_finds_no_new_cases(self, case_service, mock_repo, mock_fs):
        # Given
        mock_fs.list_directories.return_value = ["case1"]
        mock_repo.list_all.return_value = [Case(case_id="case1")]

        # When
        new_cases = case_service.scan_for_new_cases()

        # Then
        assert len(new_cases) == 0
        mock_repo.add.assert_not_called()

    def test_update_case_status(self, case_service, mock_repo):
        # Given
        case = Case(case_id="case1")
        mock_repo.get.return_value = case

        # When
        case_service.update_case_status("case1", CaseStatus.PROCESSING)

        # Then
        mock_repo.get.assert_called_once_with("case1")
        # The case object's status should be updated
        assert case.status == CaseStatus.PROCESSING
        # And the repository's update method should be called with the modified object
        mock_repo.update.assert_called_once_with(case)
