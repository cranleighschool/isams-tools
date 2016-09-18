import logging
import ssl
from ldap3 import Server, Connection, NTLM, SUBTREE, ALL_ATTRIBUTES, extend, LDAPSocketOpenError, Tls
from settings import AD_SERVER, AD_USERNAME, AD_PASSWORD, AD_SEARCH_BASE

logger = logging.getLogger('root')


class ADConnection():
    server = None
    connection = None

    def __init__(self):
        try:
            # tls = Tls(local_private_key_file='root.cer', local_certificate_file='root.cer',
            #           validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca_certs.b64')
            self.server = Server(AD_SERVER)
            # self.server = Server(AD_SERVER, use_ssl=True, tls=tls)
            # tls = Tls(validate=ssl.CERT_REQUIRED,
            #         ca_certs_file = 'root.cer')
            self.connection = Connection(self.server, user=AD_USERNAME, password=AD_PASSWORD, authentication=NTLM)
            if not self.connection.bind():
                print('error in bind', self.connection.result)
        except LDAPSocketOpenError as e:
            logger.critical("Could not connect to AD server: " + str(e))

    def search_by_username(self, username):
        self.connection.search(search_base=AD_SEARCH_BASE,
                 search_filter='(&(sAMAccountName={0}))'.format(username),
                 search_scope=SUBTREE,
                 attributes=ALL_ATTRIBUTES,
                 get_operational_attributes=True)

        return self.connection.response

    # def search_by_all_details(self, username, email, ):

    def search_by_guid(self, guid):
        self.connection.search(search_base=AD_SEARCH_BASE,
                 search_filter='(&(objectGUID={0}))'.format(guid),
                 search_scope=SUBTREE,
                 attributes=ALL_ATTRIBUTES,
                 get_operational_attributes=True)

        return self.connection.response

    def add_user(self, username, email, forename, surname):
        user = "CN={0} {1},{2}".format(forename, surname, AD_SEARCH_BASE)
        self.connection.add(user, attributes={'objectClass': ['top', 'person', 'organizationalPerson', 'user'], 'sAMAccountName': username, 'givenName': "{0} {1}".format(forename, surname)})

        # TODO: can't modify password without SSL
        # extend.microsoft.modifyPassword.modify_ad_password(self.connection, user, None, username)
        return self.connection.result


