import logging
import psycopg2
import psycopg2.extras
import requests
from datetime import datetime

from isams_tools.models import Form, Student, Teacher, Department, Set, SetList, Subject, YearGroup
from settings import SCF

logger = logging.getLogger('root')

class SCFConnector():
    STUDENT_TABLE = 'scf_student'

    host = None
    user = None
    password = None
    database = None

    cursor = None
    connection = None

    # define our own contains so we can check "if student in scf_connection"
    def __contains__(self, item):
        if type(item) is Student:
            query = "SELECT id FROM scf_student WHERE sync_value = %s"
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

        self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM scf_student")
        students = self.cursor.fetchall()
        student_list = []
        for student in students:
            new_student = Student(student.first_name, student.last_name, student.username, student.email,
                                  student.year_id, student.form_id, student.date_of_birth, student.gender,
                                  student.sync_value)

            student_list.append(new_student)

        return student_list

    # def get_student(self, sync_value):
    #     print(api_call('student', 'get', {}))

    def get_student_from_id(self, id):
        self.cursor.execute("SELECT * FROM scf_students WHERE id = %s")
        result = self.cursor.fetchone()
        student = None

        if result:
            student = Student(student.first_name, student.last_name, student.username, student.email,
                    student.year_id, student.form_id, student.date_of_birth, student.gender,
                    student.sync_value)

        return student


    def get_year_group_id(self, nc_year):
        query = 'SELECT id FROM "scf_yeargroup" WHERE nc_year = %s'

        year_group_id = None
        self.cursor.execute(query, (nc_year,))

        results = self.cursor.fetchall()
        if results:
            row = results[0]
            year_group_id = row.id
        else:
            logger.warning("No year group found for for " + str(nc_year))
        return year_group_id

    def get_form_id(self, form_name):
        query = 'SELECT id FROM "scf_form" WHERE name = %s'
        form_id = None
    
        self.cursor.execute(query, (form_name,))
        results = self.cursor.fetchall()
        if results:
            row = results[0]
            form_id = row.id
        else:
            logger.warning("No form found with name " + str(form_name))

        return form_id

    def exact_student_exists(self, student):
        at_school = True

        if student.status != 1:
            at_school = False

        year_group_id = self.get_year_group_id(student.nc_year)
        form_id = self.get_form_id(student.form)

        params = (student.forename, student.surname)

        query = 'SELECT * FROM "scf_student'
        query += 'WHERE first_name = %s'
        query += 'AND last_name = %s'

        if student.date_of_birth:
            query += 'AND date_of_birth = %s'
            params.append(student.date_of_birth)
        else:
            query += 'AND date_of_birth IS NULL'

        if student.username:
            query += 'AND username = %s'
            params.append(student.username)
        else:
            query += 'AND username IS NULL'

        if student.email:
            query += 'AND email = %s'
            params.append(student.email)
        else:
            query += 'AND email IS NULL'

        if student.form.sync_value
            query += 'AND form_id = %s'
            params.append(student.form.sync_value)
        else:
            query += 'AND form_id = %s'

        if year_group_id:
            query += 'AND year_id = %s'
            params.append(year_group_id)
        else:
            query += 'AND year_id IS NULL'

        query += 'AND status = %s'
        query += 'WHERE sync_value = %s'

        params.append(at_school, student.sync_value)

        return self.cursor.execute(query, params)

    def update_student(self, student):
        query = """UPDATE "scf_student"
                          SET first_name = %s
                          , last_name = %s
                          , date_of_birth = %s
                          , username = %s
                          , email = %s
                          , form_id = %s
                          , year_id = %s
                          , at_school = %s
                          WHERE sync_value = %s"""

        at_school = True

        if student.status != 1:
            at_school = False

        year_group_id = self.get_year_group_id(student.nc_year)
        form_id = self.get_form_id(student.form)

        params = (student.forename, student.surname, student.date_of_birth, student.username, student.email,
                  form_id, year_group_id, at_school, student.sync_value)

        self.cursor.execute(query, params)
        self.connection.commit()

    def get_all_teachers(self):
        self.cursor.execute("SELECT * FROM scf_web_staff, auth_user WHERE scf_web_staff.user_id=auth_user.id")
        teachers = self.cursor.fetchall()
        teacher_list = []
        for teacher in teachers:
          if teacher.is_active == 'true':
              status = 1
          else:
              status = -1
              new_teacher = Teacher(teacher.forename, teacher.surname, teacher.title, teacher.email, teacher.school_id, status)
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
            teacher = Teacher(row.first_name, row.last_name, row.title, row.email, row.sync_value, row.is_active)
        else:
            logger.warning("No results for " + sync_value)
        return teacher


    def add_teacher(self, teacher):
      payload = {'forename': teacher.forename, 'surname': teacher.surname, 'title': teacher.title, 'email': teacher.email, 'sync_value': teacher.sync_value, 'status': teacher.status}
      api_call('teacher', 'create', payload)

    
    def get_teacher_id(self, sync_id):
        teacher = None
        query = """SELECT user_id 
                   FROM scf_web_staff
                   WHERE sync_value='%s'
                """
        self.cursor.execute(query % sync_id)
        row = self.cursor.fetchone()
        return row.id
    

    def update_teacher(self, teacher):
        payload = {'forename': teacher.forename, 'surname': teacher.surname, 'title': teacher.title, 'email': teacher.email, 'sync_value': teacher.sync_value, 'status': teacher.status}
        api_call('teacher', 'update', payload)

    def add_form(self, form):
        payload = {'name': form.name, 'nc_year': form.nc_year, 'teacher_sync_value': form.teacher.sync_value}
        api_call('form', 'create', payload)

    def add_department(self, department):
        if department.head_of_department:
            hod = department.head_of_department.sync_value
        else:
            hod = None

        payload = {'name': department.name, 'code': department.code, 'head_of_department': hod, 'sync_value': department.sync_value}
        api_call('department', 'create', payload)

    def add_subject(self, subject):
      # FIXME HoS
      try:
          payload = {'name': subject.name, 'code': subject.code, 'department': subject.department.sync_value or None, 'head_of_subject': '', 'sync_value': subject.sync_value}
      except AttributeError:
          payload = {'name': subject.name, 'code': subject.code, 'department': None, 'head_of_subject': '', 'sync_value': subject.sync_value}
          api_call('subject', 'create', payload)


    def add_year_group(self, year_group):
        payload = {'name': year_group.name, 'code': year_group.code, 'nc_year': year_group.nc_year}
        api_call('setlist', 'create', payload)


    def add_set(self, set):
        payload = {'name': set.name, 'nc_year': set.nc_year, 'subject': set.subject, 'teacher': set.teacher.sync_value,
                   'sync_value': set.sync_value}
        api_call('set', 'create', payload)

    def get_set_from_id(self, id):
        self.cursor.execute("SELECT * FROM scf_set WHERE id = %s")
        result = self.cursor.fetchone()
        set = None

        if set:
            student = Student(set.)

        return student

    def add_setlist(self, setlist):
        try:
            payload = {'student': setlist.student.sync_value, 'set': setlist.set.sync_value, 'sync_value': setlist.sync_value,
                   'submitted_by': setlist.submitted_by, 'submitted_date': setlist.submitted_date}
        except AttributeError:
            logger.critical("Couldn't add set list with payload: {0}".format(payload))

        api_call('setlist', 'create', payload)

    def get_setlists_sync_value(self):
        query = 'SELECT sync_value "scf_web_setlist"'
        self.cursor.execute(query)

        for setlist in self.cursor.fetchall():
            yield setlist.id

    def remove_setlist(self, sync_value):
        print("About to delete setlist with id: " + str(sync_value))


def api_call(object_name, action, payload):
    r = requests.post("http://staff.cranleigh.ae/scf/api/" + action + "_" + object_name + "/1234", data=payload)

    if r.status_code != 200:
        logger.critical('Error when adding {0}: '.format(object_name) + r.text)
