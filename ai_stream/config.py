"""Configuration."""

import logging
from hydra import compose
from hydra import initialize
from omegaconf import DictConfig


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(module_name: str) -> logging.Logger:
    """Creates and returns a logger with the given module name."""
    # Create a logger with the specified module name
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    return logger


# Manually initialize Hydra
def load_config(config_name: str = "default") -> DictConfig:
    """Load the configuration for the application."""
    config_dir = "../config"
    with initialize(config_path=config_dir, job_name="my_app", version_base="1.3.2"):
        cfg = compose(config_name=config_name)

    return cfg
