import psycopg2
import psycopg2.extras

import logging
from datetime import datetime
from isams_tools.models import Form, Student, Teacher
from settings import SCF


logger = logging.getLogger('root')

class SCFConnector():
    STUDENT_TABLE = 'scf_web_pupil'

    host = None
    user = None
    password = None
    database = None

    cursor = None
    connection = None

    # define our own contains so we can check "if student in scf_connection"
    def __contains__(self, item):
        if type(item) is Student:
            query = "SELECT id FROM scf_web_pupil WHERE mis_id = %s"
            self.cursor.execute(query, (item.sync_id,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        else:
            return False


    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        pass

    def connect(self):
        conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(
            self.host, self.database, self.user, self.password)
        logger.debug("Conncting to Postgres DB with string: {0}".format(conn_string))
        self.connection = psycopg2.connect(conn_string)

        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM scf_web_pupil")
        students = self.cursor.fetchall()
        student_list = []
        for student in students:
            new_student = Student(student['first_name'], student['last_name'], student['username'], student['email'],
                                  student['year_id'], student['form_id'], student['dob'], student['gender'],
                                  student['mis_id'])

            student_list.append(new_student)

        return student_list

    def add_student(self, student):
        query = """INSERT INTO scf_web_pupil
            (first_name, last_name, date_of_birth, gender, form_id, year_id, mis_id, added, created_by_id, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (student.forename, student.surname, student.date_of_birth, student.gender, "1",  "1", student.sync_id,
                datetime.now().strftime("%Y-%m-%d"), "1", datetime.now().strftime("%Y-%m-%d"))

        self.cursor.execute(query, data)
        self.connection.commit()

    def check_student_exists(self, student):
        query = """SELECT * FROM scf_web_pupil"""


    def exact_student_exists(self, student):
        query = """SELECT * FROM scf_web_pupil
                   WHERE first_name = %s
                   AND last_name = %s
                   AND date_of_birth = %s
                   AND username = %s
                   AND email = %s
                   AND form_id = %s
                   AND year_id = %s
                   AND mis_id = %s"""
        # TODO: need to get form and year details from DB here
        data = (student.forename, student.surname, student.date_of_birth, student.username, student.email, 1, 1, student.sync_id)

        self.cursor.execute(query, data)
        student = self.cursor.fetchone()

        return student

    def update_student(self, student):
        query = """UPDATE "scf_web_pupil"
                          SET first_name = %s
                          , last_name = %s
                          , date_of_birth = %s
                          , username = %s
                          , email = %s
                          , form_id = %s
                          , year_id = %s
                          WHERE mis_id = %s"""
        # TODO: need to get form and year details from DB here
        data = (student.forename, student.surname, student.date_of_birth, student.username, student.email, 1, 1,
                student.sync_id)

        self.cursor.execute(query, data)
        self.connection.commit()
