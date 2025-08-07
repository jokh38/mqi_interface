from typing import Protocol, Optional
from .models import Task

from dataclasses import dataclass

@dataclass
class GPUStatus:
    """Represents the status of a single GPU."""
    id: int
    name: str
    memory_total: int
    memory_used: int
    utilization: int

@dataclass
class DiskUsage:
    """Represents the disk usage of a filesystem path."""
    total: int
    used: int
    free: int
    percent: float

class ISystemMonitor(Protocol):
    """An interface for a system monitor."""
    def get_cpu_usage(self) -> float:
        ...

    def get_gpu_status(self) -> list[GPUStatus]:
        ...

    def get_disk_usage(self, path: str) -> DiskUsage:
        ...

class IWorkflowOrchestrator(Protocol):
    """An interface for the main workflow orchestrator."""
    def process_new_cases(self) -> None:
        ...

class ITaskScheduler(Protocol):
    """An interface for a task scheduler."""

    def schedule_case(self, case_id: str) -> None:
        """Schedules all the necessary tasks for a given case."""
        ...

    def get_next_task(self) -> Optional[Task]:
        """Gets the next task to be executed from the queue."""
        ...

    def complete_task(self, task_id: str) -> None:
        """Marks a task as complete."""
        ...
