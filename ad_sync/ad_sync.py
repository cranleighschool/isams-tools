import logging
import os
import sqlite3
import uuid
from xml.etree import ElementTree

from settings import URL, DEBUG, AD_SYNC_ADMIN_EMAIL, AD_SERVER
from utils.ad_connection import ADConnection
from utils.connection import ISAMSConnection
from utils.isams_email import ISAMSEmail
from utils.account import Account

# # make sure this isn't called directly
# if __name__ == "__main__":
#     sys.stderr.write('Please use bin/isams_tools instead\n')
#     sys.exit(1)

logger = logging.getLogger('root')


class ADSync:
    tree = None
    db_connection = None
    ad_connection = None
    db_cursor = None
    first_run = False
    all_students = []

    dupe_error_email = '''The initial sync failed because of duplicates, you will need to rectify this in iSAMS first.
    \nError: {0}'''

    def setup_student_database(self):
        logger.info("No student DB found, creating")
        with self.db_connection:
            self.db_cursor.execute('''CREATE TABLE students
                                   (isams_id text, academic_year integer, forename text, surname text, email text, username text)''')
            self.db_connection.commit()
            # unique not primary for the rare instance students leave then return
            self.db_cursor.execute('CREATE UNIQUE INDEX students_isams_id ON students(isams_id);')
            # c.execute('CREATE UNIQUE INDEX students_email ON students(email);')
            # c.execute('CREATE UNIQUE INDEX students_username ON students(username);')
            self.db_connection.commit()

    def do_student_checks(self, first_run):
        self.first_run = first_run
        # if not self.ad_connection:
        #     self.ad_connection = ADConnection()

        last_student = None
        usernames = []
        for student in self.tree.iter('Pupil'):
            id = student.find('SchoolId').text
            username = student.find('UserName').text
            email = student.find('EmailAddress').text
            email_first_bit = email.split('@')[0]
            academic_year = student.find('NCYear').text

            if username != email_first_bit:
                print("Warning {0} != {1}".format(username, email_first_bit))
            forename = student.find('Forename').text
            surname = student.find('Surname').text

            student_details = (id, username, email, forename, surname)

            account = Account(id, forename, surname, academic_year, username, email)
            account.sync(self.first_run)


            # if not account.sync(self.first_run):
            #     self.db_connection.rollback()
            #     os.remove('ad_sync/students.db')

            self.all_students.append(student_details)

        # # clean up changes
        # if DEBUG and not self.first_run:
        #     self.db_cursor.execute('DELETE FROM students WHERE id=?', ('123456',))
        #     self.db_cursor.execute('UPDATE students SET surname=? WHERE id=?', ('Lee', '042752705547'))

        logger.debug("Total students: " + str(len(self.all_students)))

    def __init__(self):
        # create the connection to ISAMS and receive the parsed XML
        self.tree = ISAMSConnection(URL).get_tree()

        if not os.path.exists('ad_sync/students.db'):
            self.db_connection = sqlite3.connect('ad_sync/students.db', isolation_level=None)
            self.db_cursor = self.db_connection.cursor()
            self.first_run = True
            self.setup_student_database()

        #
        #     if DEBUG:
        #         self.db_cursor.execute('DELETE FROM students WHERE id=?', ('152127695781',))
        #         bloggs = ('123456', 'Joe', 'Bloggs', 'blojoe2022', 'blojoe2022@cranleigh.ae', )
        #         self.db_cursor.execute('INSERT INTO students VALUES(?, ?, ?, ?, ?)', bloggs)
        #         self.db_cursor.execute('UPDATE students SET surname=? WHERE id=?', ('Leesan', '042752705547'))
        #
        #
        #
        self.do_student_checks(self.first_run)
        self.db_connection.commit()
        self.db_connection.close()

        # a = Account("Matthew", "Zo", 13, None, None)
