from register_reminder import register_reminder as rr
from settings import DEBUG
import logging
import sys

logger = logging.getLogger('isams_tools')
hdlr = logging.FileHandler('../isams_tools.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# make sure this isn't called directly
if __name__ == "__main__":
    sys.stderr.write('Please use bin/isams_tools instead\n')
    logger.warning('Please use bin/isams_tools instead')
    sys.exit(1)

# check we've got a settings file
try:
    from settings import *
except ImportError:
    logger.warning('You have not renamed settings_example.py to settings.py\n')
    sys.stderr('You have not renamed settings_example.py to settings.py\n')
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
            rr.run()
        else:
            rr.run(kwargs['stage'])
    else:
        logger.warn("Incorrect module given")
