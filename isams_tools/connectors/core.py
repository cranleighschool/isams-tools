import logging

from isams_tools.connectors.scf import SCFConnector
from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.isams_api import iSAMSJSONConnection, iSAMSXMLConnection
from isams_tools.connectors.middle import MiddleConnection
from settings import CONNECTION_METHOD, ISAMS_DATABASE_SERVER, ISAMS_DATABASE, ISAMS_DATABASE_USER, ISAMS_DATABASE_PASS

logger = logging.getLogger('root')

class ConnectionManager:
    """Helper class to abstract away the choice of connection"""
    connection = None
    type = None

    def connect(self, connection=None):
        """Creates a suitable connection depending on settings
        :return: the connection object
        """
        if not connection:
            method = CONNECTION_METHOD
        else:
            method = connection['type']

        logger.debug("ConnectionManager.connect() using {0}".format(method))

        # FIXME: standardise the type
        if method in ['JSON', 'iSAMS_JSON']:
            self.connection = iSAMSJSONConnection()
            self.type = 'JSON'
        elif method in ['XML', 'iSAMS_XML']:
            self.connection = iSAMSXMLConnection()
            self.type = 'XML'
        elif method in ['MSSQL', 'iSAMS']:
            if not connection:
                self.connection = iSAMSConnection(ISAMS_DATABASE_SERVER, ISAMS_DATABASE_USER, ISAMS_DATABASE_PASS,
                                                  ISAMS_DATABASE)
            else:
                self.connection = iSAMSConnection(connection['server'], connection['user'], connection['password'],
                                                  connection['database'])

            self.type = 'MSSQL'
        elif method == 'scf':
                connection = SCFConnector(connection['server'], connection['user'], connection['password'], connection['database'])
        elif method == 'middle':
            connection = MiddleConnector(connection['server'], connection['user'], connection['password'], connection['database'])
        else:
            exit("Connection method not supported")

        self.connection.connect()
        return self.connection
