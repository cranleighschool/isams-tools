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

    def __contains__(self, item):



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
        self.cursor.execute("SELECT * FROM %s" % self.STUDENT_TABLE)
        students = self.cursor.fetchall()
        student_list = []
        for student in students:
            new_student = Student(student['first_name'], student['last_name'],
                    None, None, student['year_id'], student['form_id'], None, None, None)

            student_list.append(student)

        return student_list

    def add_student(self, student):
        query = """INSERT INTO scf_web_pupil
            (first_name, last_name, date_of_birth, gender, form_id, year_id, mis_id, added, created_by_id, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (student.forename, student.surname,
                            student.date_of_birth, student.gender, "1",
                            "1", student.sync_id, datetime.now().strftime("%Y-%m-%d"), "1", datetime.now().strftime("%Y-%m-%d"))

        self.cursor.execute(query, data)
        self.connection.commit()

    def check_student_exists(self, student):
        query = """SELECT * FROM scf_web_pupil"""
