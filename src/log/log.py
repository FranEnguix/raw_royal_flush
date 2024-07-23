import logging
from datetime import datetime


class CsvLogHandler(logging.StreamHandler):
    def emit(self, record):
        log_entry = self.format(record)
        with open("spade_logs.csv", "a") as f:
            f.write(f"{log_entry}\n")


def setup_logging():
    logger = logging.getLogger("spade")
    logger.setLevel(logging.INFO)
    handler = CsvLogHandler()
    formatter = logging.Formatter(
        "%(asctime)s,%(name)s,%(message)s", datefmt="%Y/%m/%d %H:%M:%S.%f"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
