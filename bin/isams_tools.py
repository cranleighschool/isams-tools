#!/usr/bin/env python3
# run this file from crontab, to run weekdays at 8am:
# 0 8 * * 1-5 /usr/bin/python3 /path/to/isams-tools/bin/isams_tools > /var/log/isams_tools.log
from register_reminder import register_reminder as rr
from settings import DEBUG
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = logging.getLogger('isams_tools')
hdlr = logging.FileHandler('../isams_tools.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# check we've got a settings file
try:
    from settings import *
except ImportError:
    logger.warning('You have not renamed settings_example.py to settings.py\n')
    sys.stderr('You have not renamed settings_example.py to settings.py\n')
    sys.exit(1)

logger.info('Started isams_tools with arguments:' + str(sys.argv))

if sys.argv[1] == "register_reminder":
    if int(sys.argv[2]) in range(1, 4):
        rr.run(int(sys.argv[2]))
    else:
        print("Incorrect stage given", file=sys.stderr)
else:
    print("Incorrect module given", file=sys.stderr)
