"""Central logging setup used by scripts and future services."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure a concise process-wide log format."""

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unknown log level: {level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

