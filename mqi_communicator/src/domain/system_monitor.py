import psutil
import logging
from .interfaces import ISystemMonitor, GPUStatus, DiskUsage

logger = logging.getLogger(__name__)

import pynvml

class SystemMonitor(ISystemMonitor):
    """
    A service that monitors system hardware resources like CPU, disk, and GPU.
    """
    def __init__(self):
        self._nvml_initialized = False
        try:
            pynvml.nvmlInit()
            self._nvml_initialized = True
            logger.info("Successfully initialized NVML for GPU monitoring.")
        except pynvml.NVMLError as e:
            logger.warning(f"Could not initialize NVML. GPU monitoring will be disabled. Error: {e}")

    def get_cpu_usage(self) -> float:
        """Returns the system-wide CPU utilization as a percentage."""
        return psutil.cpu_percent(interval=1)

    def get_disk_usage(self, path: str) -> DiskUsage:
        """
        Returns the disk usage for the filesystem of a given path.

        Args:
            path (str): The path to check disk usage for.

        Returns:
            A DiskUsage object with usage statistics in bytes.
        """
        usage = psutil.disk_usage(path)
        return DiskUsage(
            total=usage.total,
            used=usage.used,
            free=usage.free,
            percent=usage.percent
        )

    def get_gpu_status(self) -> list[GPUStatus]:
        """
        Returns the status of all available NVIDIA GPUs.

        If NVML is not available or fails, returns an empty list.
        """
        if not self._nvml_initialized:
            return []

        try:
            statuses = []
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                statuses.append(GPUStatus(
                    id=i,
                    name=name,
                    memory_total=memory_info.total,
                    memory_used=memory_info.used,
                    utilization=utilization.gpu
                ))
            return statuses
        except pynvml.NVMLError as e:
            logger.error(f"Failed to query GPU status: {e}")
            return []
