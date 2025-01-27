import logging
import sys
import os

from pydantic_settings import BaseSettings


class LogConfig(BaseSettings):
    """Config object for logging setup"""

    log_level: str = "INFO"


def setup_logging(config: LogConfig | None = None):
    """
    Setup a stream handler to stdout and a file handler
    to write to ./logs/logfile.log from the root logger for convenience
    """
    config = config or LogConfig()
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(config.log_level.upper())

    # Create a StreamHandler and set the log level
    stream_handler = logging.StreamHandler(stream=sys.stdout)

    logfolder, logfile = os.path.join(os.getcwd(), "logs"), "logfile.log"
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)
    file_handler = logging.FileHandler(f"{logfolder}/{logfile}")
    # Create a formatter for the log messages
    formatter = logging.Formatter(
        "%(asctime)s | %(processName)-10s | %(levelname)-8s | %(funcName)s | %(message)s"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Add the StreamHandler to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


logger = setup_logging()
