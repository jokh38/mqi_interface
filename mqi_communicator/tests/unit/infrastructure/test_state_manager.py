import pytest
import json
from pathlib import Path
from unittest.mock import mock_open, patch, call
from threading import Thread

from src.infrastructure.state import StateManager, StateManagerError

class TestStateManager:
    @pytest.fixture
    def state_file(self):
        # Use a real path in a temp directory to test file operations
        return Path("/tmp/test_state.json")

    @pytest.fixture
    def initial_state(self):
        return {"cases": {"case1": {"status": "NEW"}}, "jobs": {}}

    @pytest.fixture
    def initial_state_json(self, initial_state):
        return json.dumps(initial_state)

    def test_initialization_with_existing_state(self, state_file, initial_state_json):
        m = mock_open(read_data=initial_state_json)
        with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", m):
            sm = StateManager(state_file)
            assert sm.get("cases.case1.status") == "NEW"

    def test_initialization_with_no_state_file(self, state_file):
        with patch("pathlib.Path.exists", return_value=False):
            sm = StateManager(state_file)
            assert sm.get("cases") is None

    def test_set_and_get_value(self, state_file):
        m = mock_open()
        with patch("pathlib.Path.exists", return_value=False), \
             patch("builtins.open", m), \
             patch("pathlib.Path.rename"): # Mock rename to avoid file system errors
            sm = StateManager(state_file)
            sm.set("jobs.job1.status", "QUEUED")
            assert sm.get("jobs.job1.status") == "QUEUED"
            # Check if save was called via atomic write pattern
            m.assert_called_with(state_file.with_suffix('.tmp'), 'w')


    def test_transaction_commit(self, state_file, initial_state, initial_state_json):
        m = mock_open(read_data=initial_state_json)
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", m), \
             patch("pathlib.Path.rename") as mock_rename:
            sm = StateManager(state_file)
            m.reset_mock() # Reset mock after initialization

            # Act
            with sm.transaction():
                sm.set("cases.case1.status", "PROCESSING")
                sm.set("jobs.job1", {"status": "RUNNING"})

            # Assert
            # State should be updated after commit
            assert sm.get("cases.case1.status") == "PROCESSING"
            assert sm.get("jobs.job1.status") == "RUNNING"

            # Ensure save was called once on commit
            m.assert_called_once_with(state_file.with_suffix('.tmp'), 'w')
            mock_rename.assert_called_once_with(state_file)

    def test_transaction_rollback_on_exception(self, state_file, initial_state, initial_state_json):
        m = mock_open(read_data=initial_state_json)
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", m), \
             patch("pathlib.Path.rename"):
            sm = StateManager(state_file)

            original_status = sm.get("cases.case1.status")

            with pytest.raises(ValueError):
                with sm.transaction():
                    sm.set("cases.case1.status", "FAILED")
                    raise ValueError("Something went wrong")

            # State should be rolled back
            assert sm.get("cases.case1.status") == original_status
            assert sm.get("cases.case1.status") == "NEW"

    def test_get_inside_transaction(self, state_file, initial_state_json):
        m = mock_open(read_data=initial_state_json)
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", m), \
             patch("pathlib.Path.rename"):
            sm = StateManager(state_file)

            with sm.transaction():
                sm.set("new_key", "temp_value")
                assert sm.get("new_key") == "temp_value"

            # Value is persisted after transaction
            assert sm.get("new_key") == "temp_value"

    def test_nested_transaction_raises_error(self, state_file):
        with patch("pathlib.Path.exists", return_value=False):
            sm = StateManager(state_file)
            with pytest.raises(StateManagerError, match="A transaction is already in progress"):
                with sm.transaction():
                    with sm.transaction():
                        pass
