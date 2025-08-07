import queue
import threading
from contextlib import contextmanager
import paramiko

class ConnectionError(Exception):
    pass

class SSHConnectionPool:
    """
    A thread-safe pool for managing and reusing Paramiko SSH connections.

    This pool handles the creation, distribution, and recycling of SSH connections
    to a remote host. It is designed to be resilient, replacing broken connections
    automatically.

    Args:
        config (dict): A dictionary containing SSH connection parameters, including
                       'host', 'port', 'username', and authentication details
                       ('password' or 'key_file').
        pool_size (int): The maximum number of concurrent connections to maintain.

    Raises:
        ConnectionError: If the initial pool cannot be created.
    """
    def __init__(self, config: dict, pool_size: int = 5):
        if not all(k in config for k in ["host", "port", "username"]):
            raise ConnectionError("SSH config must include host, port, and username.")

        self.config = config
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        with self._lock:
            try:
                for _ in range(self.pool_size):
                    conn = self._create_connection()
                    self._pool.put(conn)
            except ConnectionError as e:
                # Wrap the specific connection error in a more general pool initialization error
                raise ConnectionError(f"Failed to create initial SSH connections: {e}")

    def _create_connection(self) -> paramiko.SSHClient:
        """
        Creates and returns a new Paramiko SSH client.

        This method explicitly uses an IPv4 socket to ensure compatibility
        across different network environments.

        Returns:
            paramiko.SSHClient: A connected SSH client.

        Raises:
            ConnectionError: If the SSH connection cannot be established.
        """
        import socket
        hostname = self.config.get("host")
        port = self.config.get("port")

        try:
            # Force IPv4 by using AF_INET
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a timeout for the connection attempt
            sock.settimeout(10)
            sock.connect((hostname, port))

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Use the existing socket. For more details on params, see:
            # https://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect
            client.connect(
                hostname=hostname,
                port=port,
                username=self.config.get("username"),
                key_filename=self.config.get("key_file"),
                password=self.config.get("password"),
                sock=sock,
                timeout=10
            )
            return client
        except (paramiko.SSHException, socket.error) as e:
            raise ConnectionError(f"Failed to establish SSH connection: {e}")

    def get_connection(self, timeout: float = 30.0) -> paramiko.SSHClient:
        """
        Retrieves a connection from the pool.

        Args:
            timeout (float): The maximum time in seconds to wait for a connection
                             to become available.

        Returns:
            paramiko.SSHClient: An active SSH client.

        Raises:
            ConnectionError: If no connection is available within the timeout.
        """
        try:
            return self._pool.get(block=True, timeout=timeout)
        except queue.Empty:
            raise ConnectionError("Timeout waiting for an SSH connection from the pool.")

    def release_connection(self, connection: paramiko.SSHClient):
        """
        Returns a connection to the pool for reuse.

        If the connection is found to be inactive or broken, it is discarded,
        and a new connection is created to maintain the pool size.

        Args:
            connection (paramiko.SSHClient): The connection to return to the pool.
        """
        if connection.get_transport() and connection.get_transport().is_active():
            self._pool.put(connection)
        else:
            # Connection is broken, create a new one to replace it
            try:
                new_conn = self._create_connection()
                self._pool.put(new_conn)
            except ConnectionError:
                # If we can't create a new one, just discard the old one
                # The pool size will shrink, but it's better than blocking
                pass

    @contextmanager
    def connection_context(self, timeout: float = 30.0):
        """
        A context manager for safely acquiring and releasing a connection.

        This is the preferred way to use connections from the pool, as it
        ensures that connections are always returned, even if errors occur.

        Usage:
            with pool.connection_context() as conn:
                conn.exec_command("ls -l")

        Args:
            timeout (float): The maximum time to wait for a connection.

        Yields:
            paramiko.SSHClient: An active SSH client.
        """
        connection = self.get_connection(timeout)
        try:
            yield connection
        finally:
            self.release_connection(connection)
