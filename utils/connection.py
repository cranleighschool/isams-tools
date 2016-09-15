import logging
from xml.etree import ElementTree
from settings import DEBUG, DEBUG_START_DATE, DEBUG_END_DATE

import requests

logger = logging.getLogger('root')


class ISAMSConnection:
    tree = None
    # Filters required by iSAMS - until the REST API is done, we have to fetch the data for all modules in one go
    filters = """<?xml version='1.0' encoding='utf-8'?>
    <Filters>
        <RegistrationManager>
            <RegistrationStatus startDate="{0}" endDate="{1}" />
        </RegistrationManager>
    </Filters>
    """

    def __init__(self, url, start_date=None, end_date=None):
        if start_date is None:
            start_date = DEBUG_START_DATE

        if end_date is None:
            end_date = DEBUG_END_DATE

        self.filters = self.filters.format(start_date, end_date)
        headers = {'Content-Type': 'application/xml'}
        r = requests.post(url, data=self.filters, headers=headers)
        logger.debug("Opening connection to: " + url)
        logger.debug("Filters: " + self.filters)
        logger.debug(r.text[:75])

        xml = r.text
        xml = xml.encode('utf16')
        tree = ElementTree.fromstring(xml)

        self.tree = tree

    def get_tree(self) -> ElementTree:
        return self.tree
