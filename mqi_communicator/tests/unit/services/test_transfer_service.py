import pytest
from unittest.mock import MagicMock

from src.infrastructure.executors import IExecutor

from src.services.transfer_service import TransferService, TransferError

class TestTransferService:
    @pytest.fixture
    def mock_executor(self) -> MagicMock:
        return MagicMock(spec=IExecutor)

    @pytest.fixture
    def transfer_service(self, mock_executor) -> TransferService:
        return TransferService(
            remote_executor=mock_executor,
            local_data_path="/local/data",
            remote_workspace="/remote/workspace"
        )

    def test_upload_case_success(self, transfer_service, mock_executor):
        # Given
        mock_executor.execute.return_value = (0, "success", "") # Success
        case_id = "case001"

        # When
        transfer_service.upload_case(case_id)

        # Then
        assert mock_executor.execute.call_count == 2
        mock_executor.execute.assert_any_call("mkdir -p /remote/workspace")
        mock_executor.execute.assert_any_call("scp -r /local/data/case001 /remote/workspace/case001")

    def test_upload_case_failure(self, transfer_service, mock_executor):
        # Given
        mock_executor.execute.return_value = (1, "", "Permission denied") # Failure
        case_id = "case001"

        # When / Then
        with pytest.raises(TransferError, match="Failed to create remote directory for case case001: Permission denied"):
            transfer_service.upload_case(case_id)

    def test_download_results_success(self, transfer_service, mock_executor):
        # Given
        mock_executor.execute.return_value = (0, "success", "") # Success
        case_id = "case001"

        # When
        transfer_service.download_results(case_id)

        # Then
        expected_command = "scp -r /remote/workspace/case001/results /local/data/case001/results"
        mock_executor.execute.assert_called_once_with(expected_command)

    def test_download_results_failure(self, transfer_service, mock_executor):
        # Given
        mock_executor.execute.return_value = (1, "", "No such file") # Failure
        case_id = "case001"

        # When / Then
        with pytest.raises(TransferError, match="Failed to download results for case001: No such file"):
            transfer_service.download_results(case_id)
