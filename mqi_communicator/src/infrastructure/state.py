import threading
import json
from pathlib import Path
from contextlib import contextmanager
import copy
from .json_encoder import CustomJsonEncoder

class StateManagerError(Exception):
    """Custom exception for StateManager errors."""
    pass

class StateManager:
    """
    Manages the application's state in a thread-safe manner,
    persisting it to a JSON file.
    """
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._lock = threading.RLock()
        self._state: dict = {}
        self._transaction_state: dict | None = None
        self._load_state()

    def _load_state(self):
        with self._lock:
            if self.state_path.exists():
                try:
                    with open(self.state_path, 'r') as f:
                        self._state = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    raise StateManagerError(f"Failed to load state file: {e}")
            else:
                self._state = {}

    def _save_state(self):
        with self._lock:
            temp_path = self.state_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'w') as f:
                    json.dump(self._state, f, indent=2, cls=CustomJsonEncoder)
                temp_path.rename(self.state_path)
            except IOError as e:
                raise StateManagerError(f"Failed to save state file: {e}")

    def get(self, key: str, default=None):
        with self._lock:
            target_state = self._transaction_state if self._transaction_state is not None else self._state
            keys = key.split('.')
            value = target_state
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default

            # Simulate a serialization/deserialization round trip to ensure
            # that the returned object is not a "live" Python object with
            # unserializable types.
            if value is None:
                return default

            return json.loads(json.dumps(value, cls=CustomJsonEncoder))

    def set(self, key: str, value):
        with self._lock:
            target_state = self._transaction_state if self._transaction_state is not None else self._state
            keys = key.split('.')
            current = target_state
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value

            if self._transaction_state is None:
                self._save_state()

    @contextmanager
    def transaction(self):
        self.begin_transaction()
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise

    def begin_transaction(self):
        with self._lock:
            if self._transaction_state is not None:
                raise StateManagerError("A transaction is already in progress.")
            self._transaction_state = copy.deepcopy(self._state)

    def commit(self):
        with self._lock:
            if self._transaction_state is None:
                raise StateManagerError("No transaction to commit.")
            self._state = self._transaction_state
            self._transaction_state = None
            self._save_state()

    def rollback(self):
        with self._lock:
            if self._transaction_state is None:
                raise StateManagerError("No transaction to rollback.")
            self._transaction_state = None
