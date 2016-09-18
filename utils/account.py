from datetime import datetime, timedelta
from settings import USERNAME_FORMAT, USERNAME_YEAR_OFFSET, STUDENT_DOMAIN, DEBUG, AD_SYNC_ADMIN_EMAIL, BASE_DIR
from utils.ad_connection import ADConnection
from utils.isams_email import ISAMSEmail
import sqlite3

class Account:
    isams_id = None
    forename = ""
    surname = ""
    academic_year = None
    username = ""
    email = ""
    db_connection = None
    db_cursor = None

    in_sync_db = False
    in_ad = False

    def __init__(self, isams_id, forename, surname, academic_year, username, email):
        self.isams_id = isams_id
        self.forename = forename
        self.surname = surname
        self.academic_year = academic_year
        self.username = username
        self.email = email

        # open DB connection
        self.db_connection = sqlite3.connect(BASE_DIR + '/ad_sync/students.db')
        self.db_cursor = self.db_connection.cursor()

        if not username:
            self.username = self.create_username()

        if not email:
            self.email = self.username + "@" + STUDENT_DOMAIN

        ad_connection = ADConnection()
        self.in_ad = bool(ad_connection.search_by_username(username))
        self.in_sync_db = self.in_sync_db()
        # print(self.in_ad, self.in_sync_db)

    def sync(self, first_run):
        """Sync one account between iSAMS and AD, inserted and updating where necessary

        :param first_run:
        :return:
        """
        if first_run:
            if self.in_sync_db == -1:
                try:
                    self.db_cursor.execute('''INSERT INTO students(isams_id, academic_year, username, email, forename, surname)
                                    VALUES(?, ?, ?, ?, ?, ?)''', (self.isams_id, self.academic_year, self.username, self.email, self.forename, self.surname))
                    self.db_connection.commit()
                except sqlite3.Error as e:
                    print(str(e))
                    if DEBUG:
                        pass
                    else:
                        error = "Error inserting data: ", self.isams_id, self.username, self.email, self.forename, self.surname
                        self.sync_error_email = self.sync_error_email.format(error)
                        email = ISAMSEmail("[isams_tools:ad_sync] Sync Error",
                                           self.sync_error_email, AD_SYNC_ADMIN_EMAIL)
                        email.send()
                    return False

        # # check for changes and leavers
        # if not self.first_run:
        #     self.db_cursor.execute(
        #         'SELECT * FROM students WHERE (id=? AND username=? AND email=? AND forename=? AND surname=?)',
        #         student_details)
        #     exact_match = self.db_cursor.fetchone()
        #     self.db_cursor.execute('SELECT * FROM students WHERE id=?', (id,))
        #     id_match = self.db_cursor.fetchone()
        #     if id_match and not exact_match:
        #         print("Student details changed: \nOld: {0}\nNew: {1}".format(', '.join(student_details),
        #                                                                      ', '.join(id_match)))
        #     elif not (id_match and exact_match):
        #         print("Student left: " + str(student_details))
        #         pass
        # else:
        #     # we can't use executemany otherwise we can't catch the ID of the offending row in errors
        #     try:
        #         user_in_ad = self.ad_connection.search_by_username(username)
        #         if not user_in_ad:
        #             self.ad_connection.add_user(username, email, forename, surname)
        #         else:
        #             guid = uuid.UUID(bytes=(user_in_ad[0]['attributes']['objectGUID'][0]))
        #             exit(self.ad_connection.search_by_guid(guid))
        #         self.db_cursor.execute('''INSERT INTO students(id, username, email, forename, surname)
        #                         VALUES(?, ?, ?, ?, ?)''', student_details)
        #
        #
        #     except sqlite3.IntegrityError as e:
        #         if DEBUG:
        #             pass
        #         else:
        #             error = "Error inserting data: ", id, username, email, forename, surname
        #             self.sync_error_email = self.sync_error_email.format(error)
        #             email = ISAMSEmail("[isams_tools:ad_sync] Sync Error",
        #                                self.sync_error_email, AD_SYNC_ADMIN_EMAIL)
        #             email.send()
        #
        #             self.db_connection.rollback()
        #             os.remove('ad_sync/students.db')
        #             break
        #
        #     last_student = student_details
        #     self.all_students.append(str(student_details))

    def in_sync_db(self):

            self.db_cursor.execute(
                'SELECT * FROM students WHERE (isams_id=? AND username=? AND email=? AND academic_year=? AND forename=? AND surname=?)',
                (self.isams_id, self.username, self.email, self.academic_year, self.forename, self.surname))
            exact_match = self.db_cursor.fetchone()
            self.db_cursor.execute('SELECT * FROM students WHERE isams_id=?', (self.isams_id,))

            id_match = self.db_cursor.fetchone()
            if id_match and exact_match:
                return 1
            elif id_match and not exact_match:
                return 2
            elif not (id_match and exact_match):
                return -1


    def create_username(self):
        now = datetime.now()
        forename = self.forename.lower()
        surname = self.surname.lower()
        working_username = USERNAME_FORMAT

        # replace any years
        if USERNAME_YEAR_OFFSET > 0:
            offset = USERNAME_YEAR_OFFSET - self.academic_year
            if working_username.count("^") == 4:
                working_username = working_username.replace('^^^^', str(now.year + offset))
            elif working_username.count("^") == 2:
                working_username = working_username.replace('^^', str((now + timedelta(days=(365.25*offset))).strftime("%y")))
        else:
            if working_username.count("%") == 4:
                working_username = working_username.replace('%%%%', str(now.year))
            elif working_username.count("%") == 2:
                working_username = working_username.replace('%%', str(now.strftime("%y")))

        # count how many characters we need to replace for each
        leading_forename = working_username.count('!')
        trailing_forename = working_username.count('@')
        leading_surname = working_username.count('#')
        trailing_surname = working_username.count('$')

        # counting either forward or backwards from forename or surname, replace the characters
        working_username = working_username.replace('!' * leading_forename, self.forename[0:leading_forename])
        working_username = working_username.replace('@' * trailing_forename, self.forename[len(forename) - trailing_forename - 1:-1])
        working_username = working_username.replace('#' * leading_surname, self.surname[0:leading_surname])
        working_username = working_username.replace('$' * trailing_surname, self.surname[len(surname) - trailing_surname - 1:-1])

        return working_username