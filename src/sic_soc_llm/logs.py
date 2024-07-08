"""Provides logging for the project.

Used to set up file and console based loggers.
Typically called from an entry point or external script.

Typical usage:

    ```
    logger = logs.setup_logging("some_script_name")
    ```
    This will create a separate log file for the `some_script_name`.
"""

import datetime
import logging
from typing import Union
from pathlib import Path

LOG_FORMAT = "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MODULE_NAME = "sic_soc_llm"
EXTRA_MODULE_NAME = "server"
LOG_LEVEL = logging.DEBUG
DATE_STRING = f"{datetime.datetime.now().date()}"

# Logging can be used independently of configuration
LOG_DIR = Path.home() / "logs"


def setup_logging(
    script_name: str = None, log_dir: Union[Path, str] = LOG_DIR
) -> logging.Logger:
    """Set up console and file logging.

    This will create a directory to log to if it doesn't already exist.

    Safe to call in interactive environments without duplicating the logging.

    Logs on the same day will append to the same file for the same script_name.

    Args:
        script_name (str): Used in the filename for the logs.
        log_dir (Path or str): Directory to store logs in. Defaults to "~/logs".

    Returns:
        Logger object with handlers set up.
    """

    logger = logging.getLogger(MODULE_NAME)
    logger.setLevel(logging.DEBUG)

    other_logger = logging.getLogger(EXTRA_MODULE_NAME)
    other_logger.setLevel(logging.DEBUG)

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    ch.setFormatter(formatter)

    # In case this is called twice check whether a handler is already registered
    if not logger.handlers:
        logger.addHandler(ch)
        other_logger.addHandler(ch)

    try:
        if script_name is None:
            log_file = log_dir / f"{MODULE_NAME}.{DATE_STRING}.log"
        else:
            log_file = log_dir / f"{MODULE_NAME}_{script_name}.{DATE_STRING}.log"

        if len(logger.handlers) == 1:
            fh = logging.FileHandler(log_file)

            fh.setFormatter(formatter)
            fh.setLevel(LOG_LEVEL)
            logger.addHandler(fh)
            other_logger.addHandler(fh)

    except FileNotFoundError:
        logger.warning("Console logging only")

    return logger
