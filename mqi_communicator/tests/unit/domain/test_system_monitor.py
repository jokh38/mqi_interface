import pytest
from unittest.mock import MagicMock, patch

from src.domain.interfaces import GPUStatus, DiskUsage

from src.domain.system_monitor import SystemMonitor

class TestSystemMonitor:
    @pytest.fixture
    def monitor(self) -> SystemMonitor:
        return SystemMonitor()

    @patch('psutil.cpu_percent')
    def test_get_cpu_usage(self, mock_cpu_percent, monitor):
        # Given
        mock_cpu_percent.return_value = 75.5

        # When
        usage = monitor.get_cpu_usage()

        # Then
        assert usage == 75.5
        mock_cpu_percent.assert_called_once_with(interval=1)

    @patch('psutil.disk_usage')
    def test_get_disk_usage(self, mock_disk_usage, monitor):
        # Given
        mock_disk_usage.return_value = MagicMock(total=1000, used=250, free=750, percent=25.0)

        # When
        usage = monitor.get_disk_usage("/dummy")

        # Then
        assert usage.total == 1000
        assert usage.percent == 25.0
        mock_disk_usage.assert_called_once_with("/dummy")

    @patch('pynvml.nvmlDeviceGetUtilizationRates')
    @patch('pynvml.nvmlDeviceGetMemoryInfo')
    @patch('pynvml.nvmlDeviceGetName')
    @patch('pynvml.nvmlDeviceGetHandleByIndex')
    @patch('pynvml.nvmlDeviceGetCount')
    @patch('pynvml.nvmlInit')
    def test_get_gpu_status(self, mock_init, mock_count, mock_handle, mock_name, mock_mem, mock_util):
        # Given
        mock_count.return_value = 2
        mock_handle.side_effect = ["handle1", "handle2"]
        mock_name.side_effect = [b"NVIDIA A5000", b"NVIDIA A5000"]
        mock_mem.side_effect = [MagicMock(total=24576, used=1024), MagicMock(total=24576, used=2048)]
        mock_util.side_effect = [MagicMock(gpu=50), MagicMock(gpu=75)]

        monitor = SystemMonitor()

        # When
        status = monitor.get_gpu_status()

        # Then
        assert len(status) == 2
        assert status[0].name == "NVIDIA A5000"
        assert status[1].id == 1
        assert status[1].utilization == 75
        mock_init.assert_called_once()

    @patch('pynvml.nvmlInit', side_effect=__import__('pynvml').NVMLError(1))
    def test_gpu_monitoring_disabled_if_nvml_fails(self, mock_init):
        # When
        monitor = SystemMonitor() # Re-initialize to trigger the error
        status = monitor.get_gpu_status()

        # Then
        assert monitor._nvml_initialized is False
        assert status == []
