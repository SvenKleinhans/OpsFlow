import logging
from io import StringIO
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ..config.schema import LoggingConfig


class MemoryLogHandler(logging.Handler):
    """Logging handler that stores log records in an in-memory buffer."""

    def __init__(self):
        """Initializes the in-memory logging buffer."""
        super().__init__()
        self._buffer = StringIO()

    def emit(self, record: logging.LogRecord) -> None:
        """Stores a formatted log entry in the internal buffer.

        Args:
            record (logging.LogRecord): Log record to store.
        """
        self._buffer.write(self.format(record) + "\n")

    def get_value(self) -> str:
        """Returns the concatenated log messages.

        Returns:
            str: All collected log messages.
        """
        return self._buffer.getvalue()

    def clear(self) -> None:
        """Clears the stored log messages."""
        self._buffer = StringIO()


def setup_logger(config: LoggingConfig) -> tuple[logging.Logger, MemoryLogHandler]:
    """Creates and configures the application logger.

    This logger writes to a rotating file, the console, and an in-memory handler
    used for report emails.

    Args:
        config (LoggingConfig):
            Logging configuration

    Returns:
        tuple[logging.Logger, MemoryLogHandler]:
            A tuple containing the configured logger and the in-memory log handler.
    """
    log_path = Path(config.file)

    logger = logging.getLogger(log_path.stem)
    logger.setLevel(logging.DEBUG if config.debug else logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if config.debug else logging.INFO)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if config.debug else logging.INFO)
    logger.addHandler(console_handler)

    # Memory handler
    memory_handler = MemoryLogHandler()
    memory_handler.setFormatter(formatter)
    memory_handler.setLevel(logging.DEBUG if config.debug else logging.INFO)
    logger.addHandler(memory_handler)

    return logger, memory_handler
