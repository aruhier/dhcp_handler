#!/usr/bin/python2
# Author: Anthony Ruhier
# Check if IP has changed for a specific interface, and starts associated
# handlers

import os
import sys
import logging


def prepare_logger(logger):
    """
    Set logger to a default level and add a steam handler
    """
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.INFO)
    logger.addHandler(steam_handler)
    logger.setLevel(logging.INFO)
    return logger


logger = prepare_logger(logging.getLogger())
try:
    from config import SAVED_IP_PATH
except ImportError:
    logger.critical(
        "The configuration file config.py doesn't exist. Please copy the "
        "config.py.default file as config.py and launch this script again."
    )
    sys.exit(3)
from src.ip_checker import IP_Checker_Daemon


def print_help():
    print("Script to handle IP changes on different interfaces.\n")
    print("python dhcp_handler.py [option]")
    print("[option]: ")
    print("\tstart: start in background")
    print("\tstop: stop the daemon")
    print("\trestart: restart the daemon")
    print("\trun: run in foreground")
    exit()


def init_dir(path):
    """
    Create target dir, where will be saved the IP of each interface
    """
    logger = logging.getLogger()
    if not os.path.isdir(SAVED_IP_PATH):
        try:
            os.makedirs(SAVED_IP_PATH)
        except FileExistsError:
            logger.error("Error creating " + SAVED_IP_PATH + ", file already "
                         "exists. Please remove it.")
            sys.exit(1)


init_dir(SAVED_IP_PATH)
checker_daemon = IP_Checker_Daemon("/var/run/dhcp_handler.pid")

if len(sys.argv) != 2:
    print_help()
elif "start" == sys.argv[1]:
    checker_daemon.start()
elif "stop" == sys.argv[1]:
    checker_daemon.stop()
elif "restart" == sys.argv[1]:
    checker_daemon.restart()
elif "run" == sys.argv[1]:
    checker_daemon.run()
else:
    print_help()
