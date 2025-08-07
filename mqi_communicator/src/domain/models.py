from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any

class CaseStatus(Enum):
    """Enumeration for the status of a case."""
    NEW = "new"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobStatus(Enum):
    """Enumeration for the status of a job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(Enum):
    """Enumeration for the type of a task."""
    UPLOAD = "upload"
    INTERPRET = "interpret"
    BEAM_CALC = "beam_calc"
    CONVERT = "convert"
    DOWNLOAD = "download"

@dataclass
class Case:
    """
    Represents a single patient case to be processed.

    Attributes:
        case_id: Unique identifier for the case.
        status: The current status of the case, from the CaseStatus enum.
        beam_count: The number of beams to be calculated for this case.
        created_at: Timestamp when the case was first registered.
        updated_at: Timestamp of the last update to the case.
        metadata: A dictionary for storing any other relevant case information.
    """
    case_id: str
    status: CaseStatus = CaseStatus.NEW
    beam_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Job:
    """
    Represents a processing job, which is part of a case.

    Attributes:
        job_id: Unique identifier for the job.
        case_id: The ID of the case this job belongs to.
        status: The current status of the job, from the JobStatus enum.
        gpu_allocation: A list of GPU IDs allocated to this job.
        priority: The priority of the job for scheduling.
        created_at: Timestamp when the job was created.
        started_at: Timestamp when the job started processing.
        completed_at: Timestamp when the job finished processing.
    """
    job_id: str
    case_id: str
    status: JobStatus = JobStatus.PENDING
    gpu_allocation: List[int] = field(default_factory=list)
    priority: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class Task:
    """
    Represents a single, discrete task within a job.

    Attributes:
        task_id: Unique identifier for the task.
        job_id: The ID of the job this task belongs to.
        type: The type of the task, from the TaskType enum.
        parameters: A dictionary of parameters required for this task.
        status: The current status of the task.
    """
    task_id: str
    job_id: str
    type: TaskType
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending" # Simplified status for now
