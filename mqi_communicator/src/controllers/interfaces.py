from typing import Protocol, Callable

class ILifecycleManager(Protocol):
    """An interface for managing the application's lifecycle."""

    def acquire_lock(self) -> bool:
        """Acquires a process lock to ensure single instance running."""
        ...

    def release_lock(self) -> None:
        """Releases the process lock."""
        ...

    def register_shutdown_handler(self, handler: Callable) -> None:
        """Registers a handler to be called on graceful shutdown."""
        ...

class IApplication(Protocol):
    """An interface for the main application."""

    def start(self) -> None:
        """Starts the main application loop."""
        ...

    def shutdown(self) -> None:
        """Performs a graceful shutdown of the application."""
        ...
