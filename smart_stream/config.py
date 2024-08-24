"""Configuration."""

import logging


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(module_name: str) -> logging.Logger:
    """Creates and returns a logger with the given module name.

    Parameters:
    - module_name: str, the name of the module or any identifier you want to use for the logger.

    Returns:
    - logger: an instance of a configured logger with the module name.
    """
    # Create a logger with the specified module name
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    return logger
