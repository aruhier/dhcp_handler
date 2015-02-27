#!/bin/python
# Author: Anthony Ruhier

import logging
import netifaces
import os
import subprocess
import time
from src.daemon import Daemon
from config import IF, REFRESH_TIME, SAVED_IP_PATH


class IP_Checker_Daemon(Daemon):
    logger = logging.getLogger()

    def get_ip(self):
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
                self.logger.error("No IPv4 set for " + interf)
                continue
            except ValueError:
                self.logger.error(
                    "Interface " + interf + " doesn't exist (yet)")
                continue
            except Exception as e:
                self.logger.error(e)
                continue
        return ip_assoc

    def launch_handler(self, interface, ip):
        """
        Launch associated handler
        """
        handler_path = os.path.join(
            sys.path[0], "handlers", interface + ".sh"
        )
        if not os.path.isfile(handler_path):
            self.logger.info("No handler found for " + interface + ".")
            return
        try:
            subprocess.call([handler_path, ip])
        except Exception as e:
            self.logger.error("Error when launching the handler " +
                              interface + ".sh")
            self.logger.error(e)

    def check_ip_changes(self):
        """
        Get current interfaces ip and compares it with the old ones
        """
        ip_dict = self.get_ip()
        for interf, ip in ip_dict.items():
            with open(os.path.join(SAVED_IP_PATH, interf + "_ip"), "a+") as f:
                f.seek(0)
                old_ip = f.readline().rstrip(os.linesep)
                if old_ip == ip:
                    self.logger.debug(interf + " ip didn't change")
                else:
                    self.logger.info(
                        interf + ": ip changed, launching handler")
                    f.seek(0)
                    f.truncate()
                    f.write(ip + os.linesep)
                    f.close()
                    self.launch_handler(interf, ip)
                    self.logger.info(interf + ": Done")

    def run(self):
        while True:
            self.check_ip_changes()
            time.sleep(REFRESH_TIME)
