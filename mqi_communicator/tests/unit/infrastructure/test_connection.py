import pytest
from unittest.mock import MagicMock, patch, ANY
import queue
import paramiko

from src.infrastructure.connection import SSHConnectionPool, ConnectionError

class TestSSHConnectionPool:
    @pytest.fixture
    def mock_config(self):
        return {
            "host": "localhost",
            "port": 2222,
            "username": "test",
            "key_file": "/path/to/key"
        }

    @pytest.fixture
    def mock_ssh_client(self):
        with patch('paramiko.SSHClient') as mock_ssh_client_class:

            def create_mock_instance(*args, **kwargs):
                instance = MagicMock()
                transport = MagicMock()
                transport.is_active.return_value = True
                instance.get_transport.return_value = transport
                return instance

            mock_ssh_client_class.side_effect = create_mock_instance
            yield mock_ssh_client_class

    def test_pool_initialization(self, mock_config, mock_ssh_client):
        # When
        pool = SSHConnectionPool(mock_config, pool_size=3)

        # Then
        assert pool._pool.qsize() == 3
        assert mock_ssh_client.call_count == 3

    def test_get_and_return_connection(self, mock_config, mock_ssh_client):
        # Given
        pool = SSHConnectionPool(mock_config, pool_size=1)
        initial_qsize = pool._pool.qsize()

        # When
        with pool.connection_context() as conn:
            # Then
            assert conn is not None
            assert pool._pool.empty()

        assert pool._pool.qsize() == initial_qsize

    def test_get_connection_timeout(self, mock_config, mock_ssh_client):
        # Given
        pool = SSHConnectionPool(mock_config, pool_size=1)
        conn = pool.get_connection()

        # When / Then
        with pytest.raises(ConnectionError, match="Timeout waiting for an SSH connection"):
            pool.get_connection(timeout=0.1)

        # Cleanup
        pool.release_connection(conn)

    def test_broken_connection_is_replaced(self, mock_config, mock_ssh_client):
        # Given
        pool = SSHConnectionPool(mock_config, pool_size=1)

        # Simulate a broken connection
        broken_conn = pool.get_connection()
        broken_conn.get_transport().is_active.return_value = False

        # When
        pool.release_connection(broken_conn)

        # Then
        # The pool should have created a new connection to replace the broken one.
        assert pool._pool.qsize() == 1
        # The original connect call + the new one
        assert mock_ssh_client.call_count == 2

        # The new connection should be healthy
        new_conn = pool.get_connection()
        assert new_conn.get_transport().is_active() is True

    def test_initialization_failure(self, mock_config):
        # Given
        with patch('paramiko.SSHClient.connect', side_effect=paramiko.SSHException("Auth failed")):
            # When / Then
            with pytest.raises(ConnectionError, match="Failed to create initial SSH connections"):
                SSHConnectionPool(mock_config, pool_size=2)
