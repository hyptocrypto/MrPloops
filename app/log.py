import logging


def get_logger(log_file: None):
    log_level = logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = log_file or "pooping.log"
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)
    return logging.getLogger("MrPloops")
