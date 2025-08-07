from ..infrastructure.executors import IExecutor
from .interfaces import ITransferService

class TransferError(Exception):
    """Custom exception for transfer-related errors."""
    pass

class TransferService(ITransferService):
    """
    A service for orchestrating file transfers to and from a remote machine.

    Args:
        remote_executor (IExecutor): The executor for running commands on the remote host.
        local_data_path (str): The base path for local case data.
        remote_workspace (str): The base path for the remote workspace.
    """
    def __init__(
        self,
        remote_executor: IExecutor,
        local_data_path: str,
        remote_workspace: str
    ):
        self._executor = remote_executor
        self._local_path = local_data_path
        self._remote_path = remote_workspace

    def upload_case(self, case_id: str) -> None:
        """
        Uploads a case directory from the local machine to the remote workspace.

        This method first ensures the parent directory exists on the remote,
        then uses 'scp' to perform a recursive copy.

        Args:
            case_id (str): The ID of the case to upload.

        Raises:
            TransferError: If the upload fails.
        """
        local_case_path = f"{self._local_path}/{case_id}"
        remote_case_path = f"{self._remote_path}/{case_id}"

        # Ensure the remote directory exists
        mkdir_command = f"mkdir -p {self._remote_path}"
        ret_code, _, stderr = self._executor.execute(mkdir_command)
        if ret_code != 0:
            raise TransferError(f"Failed to create remote directory for case {case_id}: {stderr}")

        # Use scp for the transfer
        scp_command = f"scp -r {local_case_path} {remote_case_path}"
        ret_code, _, stderr = self._executor.execute(scp_command)
        if ret_code != 0:
            raise TransferError(f"Failed to upload case {case_id}: {stderr}")

    def download_results(self, case_id: str) -> None:
        """
        Downloads the results for a case from the remote workspace to the local machine.

        Args:
            case_id (str): The ID of the case whose results are to be downloaded.

        Raises:
            TransferError: If the download fails.
        """
        local_results_path = f"{self._local_path}/{case_id}/results"
        remote_results_path = f"{self._remote_path}/{case_id}/results"

        # Use scp for the transfer
        scp_command = f"scp -r {remote_results_path} {local_results_path}"
        ret_code, _, stderr = self._executor.execute(scp_command)
        if ret_code != 0:
            raise TransferError(f"Failed to download results for {case_id}: {stderr}")
