from ad_sync import ad_sync
from register_reminder import register_reminder
from settings import DEBUG
import logging
import os
import sys

# setup logging to file
logger = logging.getLogger('root')
logging_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'isams_tools.log')
hdlr = logging.FileHandler(logging_path)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

# log debug output when in debug mode
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# make sure this isn't called directly
if __name__ == "__main__":
    logger.critical('Please use bin/isams_tools instead')
    sys.exit(1)

# check we've got a settings file
try:
    from settings import *
except ImportError:
    logger.critical('You have not renamed settings_example.py to settings.py\n')
    sys.exit(1)

logger.info('Started isams_tools with arguments:' + str(sys.argv))


def dispatch(module, **kwargs):
    """Run the correct module

    :param module: name of the module to run
    :param kwargs: keyword arguments to pass to the module
    :return: None
    """
    if module == 'register_reminder':
        if 'stage' not in kwargs:
            register_reminder.run()
        else:
            register_reminder.run(kwargs['stage'])
    elif module == 'ad_sync':
        ad_sync.ADSync()
    else:
        logger.critical("Incorrect module given")
