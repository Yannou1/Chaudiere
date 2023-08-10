#!/usr/bin/env python
import logging
import logging.handlers
from os import path
from sys import platform as CURRENT_OS
from sys import argv as ARGV

# Logger configuration for project
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s -- %(funcName)s -- %(levelname)s -- %(message)s')

if 'win32' == CURRENT_OS:
    if path.exists("c:\\tmp\\"):
        tmp_path="c:\\tmp\\"
    elif path.exists("c:\\temp\\"):
        tmp_path = "c:\\temp\\"
    else:
        tmp_path = path.abspath(path.dirname(ARGV[0]))

    LOG_FILENAME = tmp_path + "de_dietrich.log"
else:
    LOG_FILENAME = "/tmp/de_dietrich.log"
    
handler_cfg = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=100000, backupCount=3)
handler_cfg.setLevel(logging.WARNING)
handler_cfg.setFormatter(logging.Formatter('%(asctime)s -- %(funcName)s -- %(levelname)s -- %(message)s'))
logging.getLogger('').addHandler(handler_cfg)

