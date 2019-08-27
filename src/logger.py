import logging
import os


log_file = os.path.realpath(__file__) + "/../../logs/project.log"
logging.basicConfig(
    filename=log_file,  # Define log file
    level=logging.DEBUG,  # Define default mode
    format="%(asctime)s: %(message)s",  # Define default logging format
)


def get_logger(name):
    return logging.getLogger(name)
