from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.isams_api import iSAMSJSONConnection, iSAMSXMLConnection
from settings import CONNECTION_METHOD

class ConnectionManager:
    """Helper class to abstract away the choice of connection"""
    connection = None
    type = None

    def connect(self):
        """Creates a suitable connection depending on settings
        :return: the connection object
        """
        if CONNECTION_METHOD == 'JSON':
            self.connection = iSAMSJSONConnection()
            self.type = 'JSON'
        elif CONNECTION_METHOD == 'XML':
            self.connection = iSAMSXMLConnection()
            self.type = 'XML'
        elif CONNECTION_METHOD == 'MSSQL':
            self.connection = iSAMSConnection()
            self.type = 'MSSQL'
        else:
            exit("Connection method not supported")

        self.connection.connect()
        return self.connection