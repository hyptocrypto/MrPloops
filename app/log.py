import logging

log_level = logging.INFO
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_file = "pooping.log"
logging.basicConfig(level=log_level, format=log_format, filename=log_file)
LOGGER = logging.getLogger("MrPloops")
