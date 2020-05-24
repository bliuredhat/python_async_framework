# -*- coding: utf-8 -*-

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import configparser
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

MODULE_NAME = "DEMO" # Please update this para when building a new project.

try:
    path_file = os.path.join(BASE_DIR, "etc/qrec_server.conf")
    config = configparser.ConfigParser()
    config.read(path_file)

except Exception as err:
    print(err)
    exit(1)

#log日志配置，保存七天
LOGGER = logging.getLogger('RunLogger')
LOGGER.setLevel(logging.DEBUG)
fh = TimedRotatingFileHandler( os.path.join(BASE_DIR, 'log/log.log'), when="W0", interval=1, backupCount=2)
fh.suffix = "%Y%m%d"
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(u'%(asctime)s\t%(funcName)s\t[%(levelname)s]\t%(message)s')
fh.setFormatter(formatter)
if not LOGGER.handlers:
    LOGGER.addHandler(fh)

