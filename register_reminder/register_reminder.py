import datetime as dt
import sys

from settings import *
from utils import connection
from utils.isams_email import ISAMSEmail

if __name__ == "__main__":
    sys.stderr.write('Please use bin/isams_tools instead\n')
    sys.exit(1)


def send_tutor_emails(teachers, stage):
    to = ""
    bcc = ""
    list_of_missing_registers = ""
    message = ""

    for teacher in teachers:
        bcc += teachers[teacher]['email'] + ", " if teachers[teacher]['email'] else ""
        list_of_missing_registers += '{0} {1}: {2} \n'.format(teachers[teacher]['forename'],
                                                              teachers[teacher]['surname'],
                                                              teachers[teacher]['form'])

    if str(stage) == "1":
        message = FIRST_EMAIL
    elif str(stage) == "2":
        message = SECOND_EMAIL
    elif str(stage) == "3":
        message = FINAL_EMAIL
        to = FINAL_EMAIL_TO

    message = message.replace('%list_of_missing_registers%', list_of_missing_registers)

    if DEBUG:
        to = 'kieran.hogg@gmail.com'
        message += "\n\nThis a debug email, the intented recipients were: " + bcc
        message += "\n\nStage " + str(stage)

    if to:
        email = ISAMSEmail(message, bcc, to, teachers)
    else:
        email = ISAMSEmail(message, bcc, to)

    if SEND_EMAILS:
        email.send()


class RegisterReminder:
    start_date = None
    end_date = None
    tree = None

    def __init__(self, start_date, end_date, stage):
        self.start_date = start_date
        self.end_date = end_date

        # filters that are required by iSAMS for this request
        filters = """<?xml version='1.0' encoding='utf-8'?>
        <Filters>
            <RegistrationManager>
                <RegistrationStatus startDate="{0}" endDate="{1}" />
            </RegistrationManager>
        </Filters>
        """.format(self.start_date, self.end_date)

        print("DEBUG:", filters) if DEBUG else False

        # create the connection to ISAMS and receive the parsed XML
        self.tree = connection.ISAMSConnection(URL, filters).get_tree()

        # compile a unique list of tutors with unregistered kids
        list_of_tutors = self.check_for_unregistered_students()

        # send those tutors an email to remind them
        send_tutor_emails(list_of_tutors, stage)

    def check_for_unregistered_students(self):
        print("DEBUG check_for_unregistered_students()")
        all_students = []
        reg_students = []

        for student in self.tree.iter('Pupil'):
            all_students.append(student.find('SchoolId').text)

        for leaf in self.tree.iter('RegistrationStatus'):
            reg_students.append(leaf.find('PupilId').text)

        if len(reg_students) == 0:
            sys.exit("No registrations found, chances are we shouldn't be running")

        # Remove one student if we're in debug mode
        if DEBUG:
            reg_students.pop()
            reg_students.pop()
            reg_students.pop()

            total_students = len(all_students)
            total_registered_students = len(reg_students)
            print("DEBUG: Total students: {0}".format(total_students))
            print("DEBUG: Registered students: {0}".format(total_registered_students))

        missing_students_ids = (list(set(all_students) - set(reg_students)))
        missing_students = []
        teachers = {}

        for student in missing_students_ids:
            # assuming SchoolId is unique, get the student details
            leaf = self.tree.findall('.//*[SchoolId="' + student + '"]')[0]
            student_forename = leaf.find('Forename').text
            student_surname = leaf.find('Surname').text
            student_form = leaf.find('Form').text

            # add the student details to our list
            missing_students.append(
                {'forename': student_forename,
                 'surname': student_surname,
                 'form': student_form}
            )
            # assuming FormId is unique, find the form and its teacher
            form = self.tree.findall('.//Form/[@Id="' + student_form + '"]')[0]
            tutor_id = form.get('TutorId')
            tutor = self.tree.findall('.//StaffMember/[@Id="' + tutor_id + '"]')[0]
            forename = tutor.find('Forename').text
            surname = tutor.find('Surname').text
            form_name = student_form
            email = tutor.find('SchoolEmailAddress').text

            # TODO: currenly doesn't send a list of students
            if tutor_id not in teachers:
                teachers[tutor_id] = {
                    'forename': forename,
                    'surname': surname,
                    'email': email,
                    'form': form_name}

            if DEBUG:
                print("DEBUG:", student_forename, student_surname, student_form, forename, email)

        return teachers


def run(stage):
    # do some basic checks to see if we should be running
    if ENABLED:
        if DEBUG:
            RegisterReminder("2016-09-08", "2016-09-09", stage)
        else:
            today_dt = dt.datetime.today()
            tomorrow = (today_dt + dt.timedelta(days=1)).strftime('%Y-%m-%d')
            today = today_dt.strftime('%Y-%m-%d')

            if today_dt.strftime('%Y-%m-%d') in HOLIDAYS:
                sys.exit("Today is a holiday, exiting")

            if today_dt.weekday() not in WORKING_DAYS:
                sys.exit("Today is a weekend, exiting")

            RegisterReminder(today, tomorrow, stage)
