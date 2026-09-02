"""
logger.py
---------
Lightweight logging wrapper providing --verbose / --debug output using
Python's standard logging module, styled with `rich` when available.
"""

import logging
import sys

try:
    from rich.logging import RichHandler
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


def setup_logger(name: str = "scanner", verbose: bool = False, debug: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()

    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    logger.setLevel(level)

    if _HAS_RICH:
        handler = RichHandler(show_time=False, show_path=False, markup=False)
        formatter = logging.Formatter("%(message)s")
    else:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
