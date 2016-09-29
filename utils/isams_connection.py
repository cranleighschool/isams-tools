import logging
from xml.etree import ElementTree
from settings import DEBUG, URL, DEBUG_DATA, CONNECTION_METHOD, API_KEY#, DATABASE_URL

import datetime as dt
import json
import requests
import sys

logger = logging.getLogger('root')


def get_url():
    """Constructs the connection string based on settings
    :return: the URL to connect to
    """
    if CONNECTION_METHOD == 'JSON':
        return "{0}/api/batch/1.0/json.ashx?apiKey={{{1}}}".format(URL, API_KEY)
    elif CONNECTION_METHOD == 'XML':
        return "{0}/api/batch/1.0/xml.ashx?apiKey={{{1}}}".format(URL, API_KEY)
    elif CONNECTION_METHOD == 'MSSQL':
        return DATABASE_URL
    else:
        logger.critical("Connection method not supported")
        exit(1)


class ConnectionManager:
    """Helper class to abstract away the choice of connection"""
    connection = None

    def connect(self):
        """Creates a suitable connection depending on settings
        :return: the connection object
        """
        if CONNECTION_METHOD == 'JSON':
            self.connection = iSAMSJSONConnection()
        elif CONNECTION_METHOD == 'XML':
            self.connection = iSAMSXMLConnection()
        elif CONNECTION_METHOD == 'MSSQL':
            self.connection = SQLServerConnection()
        else:
            exit("Connection method not supported")

        self.connection.connect()
        return self.connection

class APIConnection(object):
    """Parent class of the connection types, does the generic stuff"""
    data = None

    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    def connect(self):
        if DEBUG_DATA:
            logger.debug("Opening data file: " + DEBUG_DATA)
            file = open(DEBUG_DATA, 'r')
            self.data = file.read()
        else:
            if not self.start_date:
                start_date = dt.datetime.today().strftime('%Y-%m-%d')

            if not self.end_date:
                end_date = (dt.datetime.today() + dt.timedelta(days=1)).strftime('%Y-%m-%d')

            self.start_date = start_date
            self.end_date = end_date

            # as we need to get all data, even if we're not looking at register we still need the filters
            self.filters = """<?xml version='1.0' encoding='utf-8'?>
                    <Filters>
                        <RegistrationManager>
                            <RegistrationStatus startDate="{0}" endDate="{1}" />
                        </RegistrationManager>
                    </Filters>
                    """.format(self.start_date, self.end_date)

            logger.debug("Filters:" + self.filters)
            headers = {'Content-Type': 'application/xml'}
            url = get_url()
            r = requests.post(url, data=self.filters, headers=headers)
            logger.info("Opening connection to: " + get_url())
            self.data = r.text

    def get_data(self):
        return self.data


class iSAMSJSONConnection(APIConnection):
    """Object to represent a JSON specific connection"""
    data = None

    def __init__(self, url=URL, start_date=None, end_date=None):
        logger.debug("Creating JSON connector")
        super().__init__()

    def connect(self):
        logger.debug("Connecting using JSON connector")
        super().connect()
        self.data = json.loads(super().get_data())

    def get_student(self, isams_id):
        found_student = None
        print("Looking for {0}".format(isams_id))
        students = self.data['iSAMS']['PupilManager']['CurrentPupils']['Pupil']
        for student in students:
            if student['SchoolId'] == isams_id:
                form = self.get_form_from_name(student['Form'])
                found_student = ISAMSStudent(student['SchoolId'], student['Forename'], student['Surname'], student['UserName'],
                                    student['EmailAddress'], student['NCYear'], form)

        return found_student

    def get_all_students(self):
        raise NotImplementedError

    def get_form_from_name(self, form_name):
        found_form = None

        forms = self.data['iSAMS']['SchoolManager']['Forms']['Form']
        for form in forms:
            if form['Form'] == form_name:
                teacher = self.get_teacher_from_id(form['@TutorId'])
                found_form = ISAMSForm(form['Form'], teacher, form['NationalCurriculumYear'])

        return found_form

    def get_teacher_from_id(self, teacher_id):
        found_teacher = None

        teachers = self.data['iSAMS']['HRManager']['CurrentStaff']['StaffMember']
        for teacher in teachers:
            if teacher['@Id'] == teacher_id:
                found_teacher = ISAMSTeacher(teacher['@Id'], teacher['Forename'], teacher['Surname'],
                                             teacher['UserName'], teacher['SchoolEmailAddress'])

        return found_teacher

    def get_unregistered_students(self):
        unregistered_students = []
        register_entries = self.data['iSAMS']['RegistrationManager']['RegistrationStatuses']['RegistrationStatus']
        for entry in register_entries:
            if entry['Registered'] == '0' and 'Code' not in entry:
                student = self.get_student(entry['PupilId'])
                form = self.get_form_from_name(entry)
                unregistered_students.append(student)

        return unregistered_students


class iSAMSXMLConnection(APIConnection):
    """Object to represent an XML specific connection"""
    data = None
    all_students = {}
    unregistered_students = []
    filters = None
    start_date = None
    end_date = None

    def __init__(self, url=URL, start_date=None, end_date=None):
        logger.debug("Creating XML connector")
        super().__init__()

    def connect(self):
        logger.debug("Connecting using XML connector")
        super().connect()
        self.data = tree = ElementTree.fromstring(super().get_data())

    def get_data(self) -> ElementTree:
        return self.data

    def get_all_students(self):
        if DEBUG:
            print("start: get_all_students()")
        if not self.data:
            logger.critical("Can't get students as no active iSAMS connection")
            sys.exit(1)

        for this_student in self.data.findall("./PupilManager/CurrentPupils")[0]:
            isams_id = this_student.find('SchoolId').text
            forename = this_student.find('Forename').text

            surname = this_student.find('Surname').text
            username = this_student.find('UserName').text
            # username = None
            email = this_student.find('EmailAddress').text
            # email = None
            form = this_student.find('Form').text
            academic_year = this_student.find('NCYear').text
            form = self.get_form_from_name(this_student.find('Form').text)

            student = ISAMSStudent(isams_id, forename, surname, username, email, academic_year, form)
            self.all_students[isams_id] = student

        if DEBUG:
            print("end: get_all_students()")
        return self.all_students

    def get_student(self, isams_id, use_all_students=True):
        student = None
        try:
            this_student = self.data.findall("./PupilManager/CurrentPupils/Pupil[SchoolId='{0}']".format(isams_id))[0]

            forename = this_student.find('Forename').text
            surname = this_student.find('Surname').text
            username = this_student.find('UserName').text
            email = this_student.find('EmailAddress').text
            form = this_student.find('Form').text
            academic_year = this_student.find('NCYear').text
            form = self.get_form_from_name(this_student.find('Form').text)

            student = ISAMSStudent(isams_id, forename, surname, username, email, academic_year, form)

        except (IndexError, AttributeError):
            # student has left
            pass

        return student

    def get_form_from_name(self, form_name):
        form_data = self.data.findall('.//Form/[@Id="' + form_name + '"]')[0]
        tutor_id = form_data.get('TutorId')
        academic_year = form_data.find('NationalCurriculumYear').text
        logging.debug("Looking for tutor with ID {0}".format(tutor_id))

        try:
            tutor_data = self.data.findall('.//StaffMember/[@Id="' + tutor_id + '"]')[0]
            forename = tutor_data.find('Forename').text
            surname = tutor_data.find('Surname').text
            username = tutor_data.find('UserName').text
            email = tutor_data.find('SchoolEmailAddress').text
        except IndexError as e:
            # we have a invalid (e.g. left) tutor which can happen, we have to ignore this
            logging.warning(
                "Error when finding the tutor of form {0}, this needs to be fixed in iSAMS".format(form_data))
            logging.warning(str(e))

        tutor = ISAMSTeacher(tutor_id, forename, surname, username, email)
        form = ISAMSForm(form_name, tutor, academic_year)

        return form

    def get_unregistered_students(self):
        unregistered_students = []
        for register_entry in self.data.iter('RegistrationStatus'):
            registration_status = int(register_entry.find('Registered').text)
            present_code = None

            try:
                present_code = int(register_entry.find('Code').text)
            except AttributeError:
                pass

            if registration_status == 0 and not present_code:
                isams_id = register_entry.find('PupilId').text
                student = self.get_student(isams_id, False)

                # if we have a student who leaves this can sometimes be None
                if student:
                    unregistered_students.append(student)

        return unregistered_students

class SQLServerConnection():
    connection = None
    cursor = None

    def __init__(self):
        import pymssql
        print("Connection to SQL Server")
        self.connection = pymssql.connect("SQL1", "Tower", "T0werp@55", "iSAMS", as_dict=True)
        self.cursor = self.connection.cursor()

    def connect(self):
        pass

    def get_student(self):
        raise NotImplementedError

    def get_all_students(self):
        raise NotImplementedError

    def get_form_from_name(self, form_name):
        form = None
        query = """SELECT * FROM [iSAMS].[dbo].[TblSchoolManagementForms] AS f
                   WHERE f.txtForm='%s'
                """

        self.cursor.execute(query % form_name)
        row = self.cursor.fetchone()
        if row:
            teacher = self.get_teacher_from_id(row['txtFormTutor'])
            form = ISAMSForm(form_name, teacher, row['intNCYear'])

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
            teacher = ISAMSTeacher(row['User_Code'], row['Firstname'], row['Surname'], row['User_Code'],
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
            this_student = ISAMSStudent(student['txtSchoolID'], student['txtForename'], student['txtSurname'],
                                        student['txtUserName'], student['txtEmailAddress'], student['intNCYear'],
                                        form)
            unregistered_students.append(this_student)


        return unregistered_students


class ISAMSTeacher():
    id = ""
    forename = ""
    surname = ""
    username = ""
    email = ""

    def __init__(self, id, forename, surname, username, email):
        self.id = id
        self.forename = forename
        self.surname = surname
        self.username = username
        self.email = email


    def __str__(self):
        return ("({0}, {1}, {2})".format(self.forename, self.surname, self.email))


class ISAMSStudent():
    isams_id = None
    forename = ""
    surname = ""
    username = ""
    email = ""
    academic_year = None
    form = None

    def __init__(self, isams_id, forename, surname, username, email, academic_year, form):
        self.isams_id = isams_id
        self.forename = forename
        self.surname = surname
        self.username = username
        self.email = email
        self.academic_year = academic_year
        self.form = form

    def __str__(self):
        return "({0}, {1}, {2}, {3}, {4}, {5})".\
            format(self.isams_id, self.forename, self.surname, self.username, self.email, self.academic_year)

class ISAMSForm():
    name = ""
    teacher = None
    academic_year = None

    def __init__(self, name, teacher, academic_year):
        self.name = name
        self.teacher = teacher
        self.academic_year = academic_year

    def __str__(self):
        return ("({0}, {1}, {2})".format(self.name, self.teacher, self.academic_year))

