import logging

from isams_tools.connectors.active_directory import ADConnection
from isams_tools.connectors.core import ConnectionManager
from settings import DATABASE_TABLE

# # make sure this isn't called directly
# if __name__ == "__main__":
#     sys.stderr.write('Please use bin/isams_tools instead\n')
#     sys.exit(1)

logger = logging.getLogger('root')


class SyncConnector:
    left_connection = None
    our_connection = None
    cursor = None
    right_connection = None

    first_run = False
    all_students = []

    dupe_error_email = '''The initial sync failed because of duplicates, you will need to rectify this in iSAMS first.
    \nError: {0}'''

    def setup_student_database(self):
        logger.info("No student DB found, creating")
        with self.our_connection:
            self.cursor.execute('''CREATE TABLE %s
                                   (student_id smallint, isams_id nvarchar(12), academic_year tinyint,
                                   forename nvarchar(255), surname nvarchar(255), email nvarchar(255),
                                   username nvarchar(50)''', DATABASE_TABLE)
            self.our_connection.commit()
            # unique not primary for the rare instance students leave then return
            self.cursor.execute('CREATE UNIQUE INDEX students_student_id ON students(student_id);')
            self.cursor.execute('CREATE INDEX students_isams_id ON students(isams_id);')
            self.cursor.execute('CREATE UNIQUE INDEX students_email ON students(email);')
            self.cursor.execute('CREATE UNIQUE INDEX students_username ON students(username);')
            self.our_connection.commit()

    def do_student_checks(self, first_run):
        self.first_run = first_run
        # if not self.ad_connection:
        #     self.ad_connection = ADConnection()

        last_student = None
        usernames = []
        all_isams_students = self.left_connection.get_all_students()
        for isams_id in all_isams_students:
            print(all_isams_students[isams_id])
            print(self.right_connection.search_by_username(all_isams_students[isams_id].username))
            # new_student = {}
            # left_fields = {}
            # right_fields = {}
            # # combine fields, any duplicates will be taken from the left side
            # for field in self.left_connection.provides_user_fields:
            #     left_fields[field] = getattr(student, field)
            #
            # for field in self.right_connection.provides_user_fields:
            #     right_fields[field] = getattr(student, field)
            #
            # user_fields = {**left_fields, **right_fields}
            #
            # # account = Account(id, forename, surname, academic_year, username, email)
            # # account.sync(self.first_run)
            #
            # exit(print(user_fields))
            #
            # # if not account.sync(self.first_run):
            # #     self.db_connection.rollback()
            # #     os.remove('ad_sync/students.db')
            #
            # self.all_students.append(student_details)

        # # clean up changes
        # if DEBUG and not self.first_run:
        #     self.db_cursor.execute('DELETE FROM students WHERE id=?', ('123456',))
        #     self.db_cursor.execute('UPDATE students SET surname=? WHERE id=?', ('Lee', '042752705547'))

        logger.debug("Total students: " + str(len(self.all_students)))

    def __init__(self):

        self.left_connection = ConnectionManager().connect()
        # self.left_students = self.left_connection.get_all_students()
        self.right_connection = ADConnection()

        sql_connection = MSSQLConnection()
        self.our_connection = sql_connection.connection
        self.cursor = sql_connection.cursor

        query = """SELECT * FROM INFORMATION_SCHEMA.TABLES
                   WHERE TABLE_NAME = N'students'"""
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if not row:
            # self.setup_student_database()

            self.first_run = True
        self.do_student_checks(self.first_run)
        # self.db_connection.commit()

        self.our_connection.commit()
        self.our_connection.close()

        return