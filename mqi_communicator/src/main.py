import sys
import logging
from pathlib import Path

from .container import Container
from .controllers.application import Application
from .controllers.lifecycle_manager import LifecycleManager
from .infrastructure.config import ConfigManager

def setup_logging(log_file: Path):
    """Sets up basic file and console logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """The main entry point for the application."""
    # Load configuration
    # In a real app, this path might come from a command-line argument
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    config_manager = ConfigManager(config_path)
    config = config_manager.config

    # Setup logging
    log_file = Path(config["app"]["log_file"])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    setup_logging(log_file)

    # Initialize container
    container = Container()
    container.config.from_dict(config)

    # Manually create the top-level objects that are not managed by the container itself
    # but use components from it.
    pid_file = Path(config["app"]["pid_file"])
    pid_file.parent.mkdir(parents=True, exist_ok=True)

    lifecycle_manager = LifecycleManager(pid_file=pid_file)

    app = Application(
        lifecycle_manager=lifecycle_manager,
        orchestrator=container.workflow_orchestrator(),
        scan_interval=config["processing"]["scan_interval_seconds"]
    )

    # Start the application
    try:
        app.start()
    except Exception as e:
        logging.critical(f"A critical error caused the application to exit: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
