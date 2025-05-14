import logging

def get_logger(name="dilemma"):
    """
    Returns a logger with the specified name, configured for the Dilemma project.
    Ensures consistent formatting and handler setup across the project.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Or DEBUG for more verbosity
    return logger