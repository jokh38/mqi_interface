import pytest
import time
from dataclasses import dataclass
from unittest.mock import MagicMock

from src.infrastructure.resilience import (
    RetryPolicy,
    retry_on_exception,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerError
)
import time

class TestCircuitBreaker:
    def test_starts_in_closed_state(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=2)
        mock_func = MagicMock(side_effect=ValueError)

        @cb
        def decorated_func():
            mock_func()

        with pytest.raises(ValueError):
            decorated_func()
        with pytest.raises(ValueError):
            decorated_func()

        assert cb.state == CircuitState.OPEN

        with pytest.raises(CircuitBreakerError):
            decorated_func()

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        mock_func = MagicMock(side_effect=ValueError)

        @cb
        def decorated_func():
            mock_func()

        with pytest.raises(ValueError):
            decorated_func()

        assert cb.state == CircuitState.OPEN

        time.sleep(0.11)

        # It should now be half-open, so it will try the call again
        with pytest.raises(ValueError):
            decorated_func()

        assert cb.state == CircuitState.OPEN # It failed again, so it re-opens

    def test_closes_after_success_in_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        mock_func = MagicMock(side_effect=[ValueError, "Success"])

        @cb
        def decorated_func():
            return mock_func()

        with pytest.raises(ValueError):
            decorated_func()

        time.sleep(0.11)

        # First call in half-open state will succeed
        result = decorated_func()

        assert result == "Success"
        assert cb.state == CircuitState.CLOSED

class TestRetryPolicy:
    def test_success_on_first_try(self):
        # Given
        mock_func = MagicMock()
        mock_func.return_value = "success"
        policy = RetryPolicy()

        @retry_on_exception(policy)
        def decorated_func():
            return mock_func()

        # When
        result = decorated_func()

        # Then
        assert result == "success"
        mock_func.assert_called_once()

    def test_success_after_one_failure(self):
        # Given
        mock_func = MagicMock()
        mock_func.side_effect = [ValueError("Fail"), "success"]
        policy = RetryPolicy(base_delay=0.01) # Use small delay for testing

        @retry_on_exception(policy, exception_type=ValueError)
        def decorated_func():
            return mock_func()

        # When
        result = decorated_func()

        # Then
        assert result == "success"
        assert mock_func.call_count == 2

    def test_failure_after_max_attempts(self):
        # Given
        mock_func = MagicMock(side_effect=IOError("Persistent failure"))
        policy = RetryPolicy(max_attempts=3, base_delay=0.01)

        @retry_on_exception(policy, exception_type=IOError)
        def decorated_func():
            return mock_func()

        # When / Then
        with pytest.raises(IOError):
            decorated_func()

        assert mock_func.call_count == 3

    def test_exponential_backoff_delay(self, monkeypatch):
        # Given
        mock_sleep = MagicMock()
        monkeypatch.setattr(time, "sleep", mock_sleep)

        mock_func = MagicMock(side_effect=RuntimeError("Failure"))
        policy = RetryPolicy(max_attempts=4, base_delay=0.1, exponential_base=2)

        @retry_on_exception(policy, exception_type=RuntimeError)
        def decorated_func():
            return mock_func()

        # When
        with pytest.raises(RuntimeError):
            decorated_func()

        # Then
        assert mock_sleep.call_count == 3
        # 1st retry delay: 0.1 * (2**0) = 0.1
        assert mock_sleep.call_args_list[0].args[0] == pytest.approx(0.1)
        # 2nd retry delay: 0.1 * (2**1) = 0.2
        assert mock_sleep.call_args_list[1].args[0] == pytest.approx(0.2)
        # 3rd retry delay: 0.1 * (2**2) = 0.4
        assert mock_sleep.call_args_list[2].args[0] == pytest.approx(0.4)
