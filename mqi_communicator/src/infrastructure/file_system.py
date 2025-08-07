import os
from typing import List

from ..services.interfaces import IFileSystem

class LocalFileSystem(IFileSystem):
    """A concrete implementation of the file system interface for local disk."""
    def list_directories(self, path: str) -> List[str]:
        """
        Lists all the directories in a given path.

        Args:
            path (str): The path to scan.

        Returns:
            A list of directory names.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified path does not exist: {path}")

        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
