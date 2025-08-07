import pytest
import tempfile
from pathlib import Path
import json

from src.infrastructure.state import StateManager
from src.infrastructure.repositories import CaseRepository
from src.domain.models import Case, CaseStatus

class TestRepositoryIntegration:
    def test_add_case_persists_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Given
            state_file = Path(tmpdir) / "state.json"
            state_manager = StateManager(state_path=state_file)
            repo = CaseRepository(state_manager=state_manager)

            case = Case(case_id="case001", status=CaseStatus.PROCESSING)

            # When
            repo.add(case)

            # Then
            # Verify directly by reading the state file
            assert state_file.exists()
            with open(state_file, 'r') as f:
                data = json.load(f)

            assert "cases" in data
            assert "case001" in data["cases"]
            assert data["cases"]["case001"]["status"] == "processing"

            # Also verify by reading back through a new repository instance
            new_state_manager = StateManager(state_path=state_file)
            new_repo = CaseRepository(state_manager=new_state_manager)
            retrieved_case = new_repo.get("case001")

            assert retrieved_case is not None
            assert retrieved_case.status == CaseStatus.PROCESSING
