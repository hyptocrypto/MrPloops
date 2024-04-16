import logging


def get_logger(log_file: str = "pooping.log"):
    log_level = logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)
    return logging.getLogger("MrPloops")
