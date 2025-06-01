# """
# Logger Module.
#
# This module provides logging functionality for the automation framework.
# It supports configurable log levels and formats.
# """
# import logging
# import os
# import sys
# from datetime import datetime
# from pathlib import Path
#
#
# # logger.py
#
# import logging
# import os
# from datetime import datetime
# from pathlib import Path
#
# # Store log file path to reuse across sessions
# _log_file_path = None
#
# def get_logger(name):
#     """
#     Get logger instance with specified name.
#
#     Args:
#         name (str): Logger name
#
#     Returns:
#         logging.Logger: Logger instance
#     """
#     global _log_file_path
#
#     # Get log level from environment (or default to INFO)
#     log_level_str = os.getenv("LOG_LEVEL", "INFO")
#     log_level = getattr(logging, log_level_str.upper(), logging.INFO)
#
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)  # Capture all levels
#
#     if logger.handlers:
#         return logger
#
#     # Create log directory
#     log_dir = Path(__file__).parent.parent.parent / "logs"
#     log_dir.mkdir(exist_ok=True)
#
#     # Create one log file path per session
#     if not _log_file_path:
#         timestamp = datetime.now().strftime("%d_%b_%Y_%I:%M_%p")
#         _log_file_path = log_dir / f"test_execution_{timestamp}.log"
#
#     # File handler
#     file_handler = logging.FileHandler(_log_file_path,encoding="utf-8")
#     file_handler.setLevel(logging.DEBUG)
#
#     # Console handler
#     console_handler = logging.StreamHandler(sys.stdout)# avoid emojis here
#     console_handler.setLevel(log_level)  # Console shows only selected level
#
#     formatter = logging.Formatter(
#         '%(asctime)s - (%(filename)s:%(lineno)d) - [%(levelname)s] %(message)s',
#         datefmt='%d-%m-%Y %I:%M:%S %p'
#     )
#
#     file_handler.setFormatter(formatter)
#     console_handler.setFormatter(formatter)
#
#     logger.addHandler(file_handler)
#     logger.addHandler(console_handler)
#
#     return logger
import inspect
import logging
import os
from datetime import datetime


def customLogger(logLevel=logging.INFO):
    # Create the directory for logs if it doesn't exist
    log_dir = "AutoLogs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # log_dir = "AutoLogs"
    # if os.path.exists(log_dir):
    #     # Clear the records (delete all files in the folder)
    #     for file in os.listdir(log_dir):
    #         file_path = os.path.join(log_dir, file)
    #         if os.path.isfile(file_path):
    #             os.remove(file_path)
    # else:
    #     # Create the folder if it doesn't exist
    #     os.makedirs(log_dir)


    # Gets the name of the class / method from where this method is called
    stack = inspect.stack()
    loggerName = stack[1][3]
    moduleName = stack[1][1]
    logger = logging.getLogger(loggerName)
    # By default, log all messages
    logger.setLevel(logLevel)

    # Check if the logger already has handlers
    if not logger.handlers:
        current_time = datetime.strftime(datetime.now(), '%d_%m_%Y_%I_%M_%S%p')
        log_file = os.path.join(log_dir, f"Log_{current_time}.log")
        fileHandler = logging.FileHandler(log_file, mode='a',encoding = "UTF-8")
        fileHandler.setLevel(logLevel)

        #formatter = logging.Formatter('%(asctime)s - %(module)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d_%m_%Y %I:%M:%S %p')
        formatter = logging.Formatter('%(asctime)s -(%(filename)5s:%(lineno)2s)- [%(levelname)4s] %(message)s', datefmt='%d_%m_%Y %I:%M:%S %p')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    return logger