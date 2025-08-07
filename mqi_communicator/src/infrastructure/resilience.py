import time
import logging
from dataclasses import dataclass
from typing import Type, Callable

logger = logging.getLogger(__name__)

@dataclass
class RetryPolicy:
    """
    A dataclass to define the configuration for a retry mechanism.

    Args:
        max_attempts (int): The maximum number of times to try the operation.
        base_delay (float): The initial delay in seconds before the first retry.
        max_delay (float): The maximum possible delay in seconds.
        exponential_base (float): The base for the exponential backoff calculation.
    """
    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 1.0
    exponential_base: float = 2.0

import enum

class CircuitState(enum.Enum):
    """An enumeration for the states of the circuit breaker."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerError(Exception):
    """Custom exception raised when the circuit is open."""
    pass

class CircuitBreaker:
    """
    A circuit breaker implementation to prevent repeated calls to a failing service.

    This class is implemented as a decorator. It monitors the decorated function for
    failures. After a certain number of failures, the circuit "opens," and subsequent
    calls will fail immediately with a CircuitBreakerError. After a timeout period,
    the circuit enters a "half-open" state, allowing a single trial call. If that
    call succeeds, the circuit closes; otherwise, it re-opens.

    Args:
        failure_threshold (int): The number of failures required to open the circuit.
        recovery_timeout (int): The time in seconds to wait before moving to HALF_OPEN.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time = 0.0

    @property
    def state(self) -> CircuitState:
        """The current state of the circuit breaker."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time > self._recovery_timeout:
                return CircuitState.HALF_OPEN
        return self._state

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            current_state = self.state
            if current_state == CircuitState.OPEN:
                raise CircuitBreakerError("Circuit is open")

            try:
                result = func(*args, **kwargs)
                self._reset()
                return result
            except Exception as e:
                self._record_failure()
                raise e
        return wrapper

    def _reset(self):
        """Resets the circuit breaker to the CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failures = 0

    def _record_failure(self):
        """Records a failure and opens the circuit if the threshold is met."""
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()


def retry_on_exception(policy: RetryPolicy, exception_type: Type[Exception] = Exception) -> Callable:
    """
    A decorator that retries a function call based on a specified policy.

    This decorator will re-invoke the decorated function if it raises a specific
    type of exception, up to a maximum number of attempts, with an exponential
    backoff delay between retries.

    Args:
        policy (RetryPolicy): The retry policy configuration.
        exception_type (Type[Exception]): The specific exception type to catch and retry on.

    Returns:
        A wrapper function that incorporates the retry logic.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exception_type as e:
                    attempts += 1
                    if attempts >= policy.max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {policy.max_attempts} attempts. Giving up."
                        )
                        raise

                    delay = min(policy.max_delay, policy.base_delay * (policy.exponential_base ** (attempts - 1)))

                    logger.warning(
                        f"Attempt {attempts} of {policy.max_attempts} for '{func.__name__}' failed with {type(e).__name__}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
        return wrapper
    return decorator
