#!/usr/bin/python2
# Check if IP has changed for a specific interface, and starts associated
# handlers

import logging
import netifaces
import os
import subprocess
import sys

IF = ("eth0",)
OLD_IP_PATH = "/var/lib/ip_update_handler"


def prepare_logger(logger):
    """
    Set logger to a default level and add a steam handler
    """
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def init_dir(path):
    """
    Create target dir, where will be saved the IP of each interface
    """
    logger = logging.getLogger()
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
    logger = logging.getLogger()
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


def launch_handler(interface, ip):
    """
    Launch associated handler
    """
    logger = logging.getLogger()
    handler_path = os.path.join("handlers", interface + ".sh")
    if not os.path.isfile(handler_path):
        logger.info("No handler found for " + interface + ".")
        return
    try:
        subprocess.call(["handlers/" + interface + ".sh", ip])
    except Exception as e:
        logger.error("Error when launching the handler " + interface + ".sh")
        logger.error(e)


init_dir(OLD_IP_PATH)
logger = prepare_logger(logging.getLogger())
ip_dict = get_ip()
for interf, ip in ip_dict.items():
    with open(os.path.join(OLD_IP_PATH, interf + "_ip"), "r+") as f:
        old_ip = f.readline().rstrip(os.linesep)
        if old_ip == ip:
            logger.debug(interf + " ip didn't change")
        else:
            logger.debug(interf + " ip changed, launching handler")
            f.seek(0)
            f.truncate()
            f.write(ip + os.linesep)
            launch_handler(interf, ip)
