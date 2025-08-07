from pathlib import Path
from dependency_injector import containers, providers

from .infrastructure.config import ConfigManager
from .infrastructure.state import StateManager
from .infrastructure.connection import SSHConnectionPool
from .infrastructure.executors import LocalExecutor, RemoteExecutor
from .infrastructure.repositories import CaseRepository, JobRepository
from .infrastructure.file_system import LocalFileSystem
from .services.resource_service import ResourceService
from .services.case_service import CaseService
from .services.job_service import JobService
from .services.transfer_service import TransferService
from .domain.task_scheduler import TaskScheduler
from .domain.system_monitor import SystemMonitor
from .domain.workflow_orchestrator import WorkflowOrchestrator

class Container(containers.DeclarativeContainer):
    """
    The main dependency injection container for the application.

    This container is responsible for creating and wiring all the components
    of the application.
    """

    config = providers.Configuration()

    # Infrastructure
    state_manager = providers.Singleton(
        StateManager,
        state_path=providers.Factory(Path, config.app.state_file)
    )

    ssh_pool = providers.Singleton(
        SSHConnectionPool,
        config=config.ssh,
        pool_size=config.ssh.pool_size.as_int()
    )

    local_executor = providers.Singleton(LocalExecutor)
    remote_executor = providers.Singleton(RemoteExecutor, connection_pool=ssh_pool)

    file_system = providers.Singleton(LocalFileSystem)

    # Repositories
    case_repo = providers.Singleton(CaseRepository, state_manager=state_manager)
    job_repo = providers.Singleton(JobRepository, state_manager=state_manager)

    # Services
    resource_service = providers.Singleton(ResourceService, total_gpus=config.resources.gpu_count.as_int())

    case_service = providers.Singleton(
        CaseService,
        case_repository=case_repo,
        file_system=file_system,
        scan_path=config.paths.local_logdata
    )

    job_service = providers.Singleton(
        JobService,
        job_repository=job_repo,
        resource_service=resource_service
    )

    transfer_service = providers.Singleton(
        TransferService,
        remote_executor=remote_executor,
        local_data_path=config.paths.local_logdata,
        remote_workspace=config.paths.remote_workspace
    )

    # Domain
    task_scheduler = providers.Singleton(
        TaskScheduler,
        case_service=case_service,
        job_service=job_service
    )

    system_monitor = providers.Singleton(SystemMonitor)

    workflow_orchestrator = providers.Singleton(
        WorkflowOrchestrator,
        case_service=case_service,
        task_scheduler=task_scheduler
    )
