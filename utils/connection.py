import logging
import requests
from xml.etree import ElementTree

logger = logging.getLogger('isams_tools')

class ISAMSConnection:
    tree = None

    def __init__(self, url, filters):
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(url, data=filters, headers=headers)
        logger.debug("Opening connection to: " + url)
        xml = r.text
        xml = xml.encode('utf16')
        tree = ElementTree.fromstring(xml)

        self.tree = tree

    def get_tree(self) -> ElementTree:
        return self.tree
