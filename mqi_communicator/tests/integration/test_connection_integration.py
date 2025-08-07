import pytest
import paramiko

from src.infrastructure.connection import SSHConnectionPool, ConnectionError

class TestSSHConnectionPoolIntegration:
    def test_connection_to_nonexistent_server(self):
        # Given
        config = {
            "host": "localhost",
            "port": 2223,  # Use a non-standard port to avoid conflicts
            "username": "test",
            "password": "test" # Use password auth for simplicity in testing
        }

        # When / Then
        # We expect a ConnectionError that wraps a paramiko exception
        with pytest.raises(ConnectionError, match="Failed to create initial SSH connections"):
            # This will fail because it can't connect to localhost:2223
            SSHConnectionPool(config, pool_size=1)
