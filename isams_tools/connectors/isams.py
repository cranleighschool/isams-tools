import logging

import pymssql

from isams_tools.models import Form, Student, Teacher
from settings import *

logger = logging.getLogger('root')

class iSAMSConnection():
    connection = None
    cursor = None

    def __init__(self, server, user, password, database):

        try:
            self.connection = pymssql.connect(server, user, password, database, as_dict=True)
            self.cursor = self.connection.cursor()
        except pymssql.InterfaceError:
            logger.critical("Could not connect to {0} on host {1} with user {2}".format(DATABASE,
                                                                                        DATABASE_SERVER,
                                                                                        DATABASE_USER))
            exit(1)

    def connect(self):
        pass

    def get_student(self):
        raise NotImplementedError

    def get_all_students(self):
        query = "SELECT TOP 10 * FROM [iSAMS].[dbo].[TblPupilManagementPupils] WHERE intSystemStatus = 1"
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

            this_student = Student(student['txtSchoolID'], student['txtForename'], student['txtSurname'],
                                        username, email, student['intNCYear'],
                                        form, student['txtDOB'], student['txtGender'], student['txtSchoolID'])
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
            form = Form(form_name, teacher, row['intNCYear'])

        return form

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
            teacher = Teacher(row['User_Code'], row['Firstname'], row['Surname'], row['User_Code'],
                                   row['SchoolEmailAddress'])

        return teacher


    def get_unregistered_students(self):
        unregistered_students = []
        print("Getting students from SQL Server")
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
                           p.intNCYear
            FROM   [iSAMS].[dbo].[tblregistrationschoolregistrationpupils] AS r
                   INNER JOIN [iSAMS].[dbo].[tblpupilmanagementpupils] AS p
                           ON p.txtschoolid = r.txtschoolid
            WHERE  p.intsystemstatus = 1
                   AND blnRegistered = 0
                   AND intCode = NULL
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
                                   p.intNCYear
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

        if DEBUG:
            self.cursor.execute(debug_query)
        else:
            self.cursor.execute(query)

        students = self.cursor.fetchall()

        for student in students:
            form = self.get_form_from_name(student['txtform'])
            this_student = Student(student['txtSchoolID'], student['txtForename'], student['txtSurname'],
                                        student['txtUserName'], student['txtEmailAddress'], student['intNCYear'],
                                        form)
            unregistered_students.append(this_student)


        return unregistered_students