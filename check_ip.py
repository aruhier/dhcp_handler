#!/usr/bin/python2
# Check if IP has changed for a specific interface, and starts associated
# handlers

import logging
import netifaces
import os
import sys

IF = ("eth0",)
OLD_IP_PATH = "/var/lib/ip_update_handler"


def prepare_logger(logger):
    """
    Set logger to a default level and add a steam handler
    """
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.INFO)
    logger.addHandler(steam_handler)
    logger.setLevel(logging.INFO)
    return logger


def init_dir(path):
    """
    Create target dir, where will be saved the IP of each interface
    """
    if not os.path.isdir(OLD_IP_PATH):
        try:
            os.makedirs(OLD_IP_PATH)
        except FileExistsError:
            logger.error("Error creating " + OLD_IP_PATH + ", file already "
                    "exists. Please remove it.")
            sys.exit(1)


def get_ip():
    """
    Get the 1st IPv4 associated to each interface in IF
    """
    ip_assoc = dict()
    for interf in IF:
        try:
            ip_assoc[interf] = (
                netifaces.ifaddresses(interf)[netifaces.AF_INET][0]["addr"]
            )
        except IndexError:
            logger.error("No IPv4 set for " + interf)
            continue
        except ValueError:
            logger.error("Interface " + interf + " doesn't exist (yet)")
            continue
        except Exception as e:
            logger.error(e)
            continue
    return ip_assoc


init_dir(OLD_IP_PATH)
logger = prepare_logger(logging.getLogger())
ip_dict = get_ip()
for interf, ip in ip_dict.items():
    with open(os.path.join(OLD_IP_PATH, interf + "_ip"), "w+") as f:
        old_ip = f.read()
        if old_ip == ip:
            logger.debug(interf + " ip didn't change")
        else:
            logger.debug(intef + " ip changed, launching handler")
