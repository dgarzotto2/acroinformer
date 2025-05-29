import logging

def configure_logging(level: str = "INFO"):
    """
    Call early in your app (before any imports that log).
    """
    fmt = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)