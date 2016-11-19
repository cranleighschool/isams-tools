import psycopg2
import psycopg2.extras
import requests

import logging
from datetime import datetime
from isams_tools.models import Form, Student, Teacher, Department, Set, SetList, Subject, YearGroup
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
            query = "SELECT id FROM scf_web_pupil WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        elif type(item) is Teacher:
            query = "SELECT id FROM scf_web_staff WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        elif type(item) is Form:
          query = "SELECT id from scf_web_form WHERE name = %s"
          self.cursor.execute(query, (item.name,))
          if self.cursor.fetchone():
              return True
          else:
            return False
        elif type(item) is Department:
            query = "SELECT id from scf_web_department WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
            if self.cursor.fetchone():
                return True
            else:
              return False
        elif type(item) is Subject:
            query = "SELECT id from scf_web_subject WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
            if self.cursor.fetchone():
                return True
            else:
              return False
        elif type(item) is YearGroup:
            query = "SELECT id from scf_web_yeargroup WHERE nc_year = %s"
            self.cursor.execute(query, (item.nc_year,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        elif type(item) is Set:
            query = "SELECT id from scf_web_set WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        elif type(item) is SetList:
            query = "SELECT id from scf_web_setlist WHERE sync_value = %s"
            self.cursor.execute(query, (item.sync_value,))
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

        self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM scf_web_pupil")
        students = self.cursor.fetchall()
        student_list = []
        for student in students:
            new_student = Student(student['first_name'], student['last_name'], student['username'], student['email'],
                                  student['year_id'], student['form_id'], student['date_of_birth'], student['gender'],
                                  student['mis_id'])

            student_list.append(new_student)

        return student_list

    def add_student(self, student):
        if not student.form:
            form = None
        else:
            form = student.form.name

        payload = {'forename': student.forename, 'surname': student.surname, 'form': form,
                   'date_of_birth': student.date_of_birth, 'email': student.email, 'sync_value': student.sync_value,
                   'gender': student.gender, 'status': student.status, 'nc_year': student.nc_year}
        r = requests.post("http://staff.cranleigh.ae/scf/api/create_student/1234", data=payload)
        if r.status_code != 200:
            logger.critical('Error when adding student: ' + r.text[:500])

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

    def get_all_teachers(self):
        self.cursor.execute("SELECT * FROM scf_web_staff, auth_user WHERE scf_web_staff.user_id=auth_user.id")
        teachers = self.cursor.fetchall()
        teacher_list = []
        for teacher in teachers:
          if teacher['is_active'] == 'true':
              status = 1
          else:
              status = -1
              new_teacher = Teacher(teacher['forename'], teacher['surname'], teacher['title'], teacher['email'], teacher['school_id'], status)
              teacher_list.append(new_teacher)

        return teacher_list


    def get_teacher(self, sync_value):
        self.cursor.execute("""SELECT u.first_name
        	,u.last_name
        	,s.title
        	,u.email
        	,s.sync_value
        	,u.is_active
            FROM scf_web_staff as s, auth_user as u
            WHERE s.sync_value=%s
            AND u.id=s.user_id
            """
            , (sync_value,))
        teacher = None
        results = self.cursor.fetchall()
        if results:
            # have to use fetchall to get it as a dict
            row = results[0]
            teacher = Teacher(row['first_name'], row['last_name'], row['title'], row['email'], row['sync_value'], row['is_active'])
        else:
            logger.warning("No results for " + sync_value)
        return teacher


    def add_teacher(self, teacher):
      payload = {'forename': teacher.forename, 'surname': teacher.surname, 'title': teacher.title, 'email': teacher.email, 'sync_value': teacher.sync_value, 'status': teacher.status}
      headers = {'X-Requested-With': ': XMLHttpRequest-type'}

      r = requests.post("http://staff.cranleigh.ae/scf/api/create_teacher/1234", data=payload, headers=headers)
      if r.status_code != 200:
          logger.critical('Error when adding teacher: ' + r.text[:500])
    
    def get_teacher_id(self, sync_id):
        teacher = None
        query = """SELECT user_id 
                   FROM scf_web_staff
                   WHERE sync_value='%s'
                """
        self.cursor.execute(query % user_code)
        row = self.cursor.fetchone()
        return row['id']
    

    def update_teacher(self, teacher):
        payload = {'forename': teacher.forename, 'surname': teacher.surname, 'title': teacher.title, 'email': teacher.email, 'sync_value': teacher.sync_value, 'status': teacher.status}

        r = requests.post("http://staff.cranleigh.ae/scf/api/update_teacher/1234", data=payload)
        if r.status_code != 200:
            logger.critical('Error when updating teacher: ' + r.text)

    def add_form(self, form):
        payload = {'name': form.name, 'nc_year': form.nc_year, 'teacher_sync_value': form.teacher.sync_value}

        r = requests.post("http://staff.cranleigh.ae/scf/api/create_form/1234", data=payload)
        if r.status_code != 200:
            logger.critical('Error when adding form: ' + r.text)

    def add_department(self, department):
        if department.head_of_department:
            hod = department.head_of_department.sync_value
        else:
            hod = None

        payload = {'name': department.name, 'code': department.code, 'head_of_department': hod, 'sync_value': department.sync_value}

        r = requests.post("http://staff.cranleigh.ae/scf/api/create_department/1234", data=payload)
        if r.status_code != 200:
            logger.critical('Error when adding departments: ' + r.text)

    def add_subject(self, subject):
      # FIXME HoS
      try:
          payload = {'name': subject.name, 'code': subject.code, 'department': subject.department.sync_value or None, 'head_of_subject': '', 'sync_value': subject.sync_value}
      except AttributeError:
          payload = {'name': subject.name, 'code': subject.code, 'department': None, 'head_of_subject': '', 'sync_value': subject.sync_value}

      r = requests.post("http://staff.cranleigh.ae/scf/api/create_subject/1234", data=payload)
      if r.status_code != 200:
          logger.critical('Error when adding subject: ' + r.text)


    def add_year_group(self, year_group):
        payload = {'name': year_group.name, 'code': year_group.code, 'nc_year': year_group.nc_year}
        r = requests.post("http://staff.cranleigh.ae/scf/api/create_year_group/1234", data=payload)
        if r.status_code != 200:
            logger.critical('Error when adding year group: ' + r.text)


    def add_set(self, set):
        payload = {'name': set.name, 'nc_year': set.nc_year, 'subject': set.subject, 'teacher': set.teacher.sync_value,
                   'sync_value': set.sync_value}
        r = requests.post("http://staff.cranleigh.ae/scf/api/create_set/1234", data=payload)

        if r.status_code != 200:
            logger.critical('Error when set: ' + r.text)


    def add_setlist(self, setlist):
        try:
            payload = {'student': setlist.student.sync_value, 'set': setlist.set.sync_value, 'sync_value': setlist.sync_value,
                   'submitted_by': setlist.submitted_by, 'submitted_date': setlist.submitted_date}
        except AttributeError:
            logger.critical("Couldn't add set list with payload: {0}".format(payload))
        r = requests.post("http://staff.cranleigh.ae/scf/api/create_setlist/1234", data=payload)

        if r.status_code != 200:
            logger.critical('Error when set: ' + r.text)

