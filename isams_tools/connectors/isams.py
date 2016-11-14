import logging
import pymssql

from isams_tools.models import Form, Student, Teacher
from settings import *

logger = logging.getLogger('root')

class iSAMSConnection():
    connection = None
    cursor = None
    STUDENT_TABLE = "TblPupilManagementPupils"

    def __init__(self, server, user, password, database):

        try:
            self.connection = pymssql.connect(server, user, password, database, as_dict=True)
            self.cursor = self.connection.cursor()
        except pymssql.InterfaceError:
            logger.critical("Could not connect to {0} on host {1} with user {2}".format(database, server, user))
            exit(1)

    def __contains__(self, item):
        if type(item) is Student:
            student = self.get_student(item.sync_id)
            return bool(student)
        else:
            raise NotImplementedError

    def connect(self):
        pass

    def get_student(self, isams_id):
        query = "SELECT * FROM [iSAMS].[dbo].[TblPupilManagementPupils] WHERE txtSchoolID = %s"
        self.cursor.execute(query, (isams_id,))
        student = self.cursor.fetchone()
        if student:
            form = self.get_form_from_name(student['txtForm'])
            try:
                username = student['txtUserName']
                email = student['txtEmailAddress']
            except KeyError:
                pass
            finally:
                username = None
                email = None

            this_student = Student(sync_value=student['txtSchoolID'], forename=student['txtForename'],
                                   surname=student['txtSurname'],username=username, email=email,
                                   nc_year=student['intNCYear'], form=form, date_of_birth=student['txtDOB'],
                                   gender=student['txtGender'])
            return this_student
        else:
            return None

    def get_all_students(self):
        query = "SELECT * FROM [iSAMS].[dbo].[TblPupilManagementPupils] WHERE intSystemStatus = 1"
        self.cursor.execute(query)
        students = self.cursor.fetchall()
        student_list = []

        # convert them into our internal representation
        for student in students:
            form = self.get_form_from_name(student['txtForm'])
            # not all students have usernames and emails set
            try:
                username = student['txtUserName']
                email = student['txtEmailAddress']
            except KeyError:
                pass
            finally:
                username = None
                email = None

            this_student = Student(forename=student['txtForename'], surname=student['txtSurname'],
                                   username=username, email=email, nc_year=student['intNCYear'],
                                   form=form, date_of_birth=student['txtDOB'],gender=student['txtGender'],
                                   sync_value=student['txtSchoolID'])
            student_list.append(this_student)

        return student_list

    def get_form_from_name(self, form_name):
        form = None
        query = """SELECT * FROM [iSAMS].[dbo].[TblSchoolManagementForms] AS f
                   WHERE f.txtForm='%s'
                """

        self.cursor.execute(query % form_name)
        row = self.cursor.fetchone()
        if row:
            teacher = self.get_teacher_from_id(row['txtFormTutor'])
            form = Form(name=form_name, teacher=teacher, nc_year=row['intNCYear'])

        return form

    def get_all_teachers(self):
            query = "SELECT person.* from staff INNER JOIN person ON staff.person_id = person.id"
            self.cursor.execute(query)
            teachers = self.cursor.fetchall()

            for teacher in teachers:
                this_teacher = Teacher(forename=teacher['forename'], surname=teacher['surname'], title=teacher['title'],
                                       email=teacher['email'], sync_value=teacher['school_id'])
                yield this_teacher

    def get_teacher_from_id(self, user_code):
        # the FK in forms is User_Code, so we have to use that
        teacher = None
        query = """SELECT *
                   FROM [iSAMS].[dbo].[TblStaff] AS s
                   WHERE s.User_Code='%s'
                """
        self.cursor.execute(query % user_code)
        row = self.cursor.fetchone()
        if row:
            teacher = Teacher(id=row['TblStaffID'], forename=row['Firstname'], surname=row['Surname'],
                              sync_value=row['User_Code'], email=row['SchoolEmailAddress'])

        return teacher


    def get_unregistered_students(self):
        unregistered_students = []
        logger.info("Getting students from SQL Server")
        query = """
            SELECT DISTINCT( tblregistrationschoolregistrationpupilsid ),
                           r.intcode,
                           r.blnregistered,
                           p.txtforename,
                           p.txtsurname,
                           p.txtform,
                           p.txtSchoolID,
                           p.txtEmailAddress,
                           p.txtUserName,
                           p.intNCYear,
                           p.txtDOB,
                           p.txtGender
            FROM   [iSAMS].[dbo].[tblregistrationschoolregistrationpupils] AS r
                   INNER JOIN [iSAMS].[dbo].[tblpupilmanagementpupils] AS p
                           ON p.txtschoolid = r.txtschoolid
            WHERE  p.intsystemstatus = 1
                   AND blnRegistered = 'false'
                   AND intCode is NULL
                   AND intregister = (SELECT tblregistrationschoolregistrationregisterid
                                      FROM
                                       [iSAMS].[dbo].[tblregistrationschoolregistrationregister]
                                                      WHERE
                                       [tblregistrationschoolregistrationregister].intregistrationdatetime =
                                       (
                                           SELECT
                                           TOP(1) [tblregistrationschoolregistrationdatetimeid]
                                           FROM
                                                   [iSAMS].[dbo].[tblregistrationschoolregistrationdatetime]
                                           WHERE
                                                   CONVERT(DATE, txtdatetime) = CONVERT(DATE, Getdate())
                                           ORDER  BY
                                                   txtdatetime ASC)
                                        )
        """

        debug_query = """
                    SELECT DISTINCT( tblregistrationschoolregistrationpupilsid ),
                                   r.intcode,
                                   r.blnregistered,
                                   p.txtForename,
                                   p.txtSurname,
                                   p.txtform,
                                   p.txtSchoolID,
                                   p.txtEmailAddress,
                                   p.txtUserName,
                                   p.intNCYear,
                                   p.txtDOB,
                                   p.txtGender
                    FROM   [iSAMS].[dbo].[tblregistrationschoolregistrationpupils] AS r
                           INNER JOIN [iSAMS].[dbo].[tblpupilmanagementpupils] AS p
                                   ON p.txtschoolid = r.txtschoolid
                    --WHERE 1=1
                    WHERE  p.intsystemstatus = 1
                           -- AND blnRegistered = 0
                           -- AND intCode = NULL
                           AND intregister = (SELECT tblregistrationschoolregistrationregisterid
                                              FROM
                               [iSAMS].[dbo].[tblregistrationschoolregistrationregister]
                                              WHERE
                               [tblregistrationschoolregistrationregister].intregistrationdatetime =
                               (
                               SELECT
                               TOP(1) [tblregistrationschoolregistrationdatetimeid]
                               FROM
                                       [iSAMS].[dbo].[tblregistrationschoolregistrationdatetime]
                               WHERE
                                       CONVERT(DATE, txtdatetime) = CONVERT(DATE, Getdate())
                               ORDER  BY
                                       txtdatetime ASC))
                """

        self.cursor.execute(query)

        students = self.cursor.fetchall()
        for student in students:
            form = self.get_form_from_name(student['txtform'])
            try:
                username = student['txtUserName']
                email = student['txtEmailAddress']
            except KeyError:
                pass
            finally:
                username = None
                email = None
            
            this_student = Student(sync_value=student['txtSchoolID'], forename=student['txtforename'],
                                   surname=student['txtsurname'], username=username, email=email,
                                   nc_year=student['intNCYear'], form=form, date_of_birth=student['txtDOB'],
                                   gender=student['txtGender'])
            unregistered_students.append(this_student)
        return unregistered_students
