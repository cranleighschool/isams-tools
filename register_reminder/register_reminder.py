import datetime as dt
import logging
import sys

from settings import *
from utils import connection
from utils.isams_email import ISAMSEmail

# make sure this isn't called directly
if __name__ == "__main__":
    sys.stderr.write('Please use bin/isams_tools instead\n')
    sys.exit(1)

logger = logging.getLogger('root')


def send_tutor_emails(teachers, stage):
    """Prepares the email list and email templates in order to send them

    :param teachers: the list of teacher dicts to send the email to, containing email, forename, surname, form
    :param stage: which stage email to send
    :return: None
    """
    bcc = ""
    list_of_missing_registers = ""
    message = ""

    # compile the BCC list as well as the text for %list_of_missing_registers%
    i = 0
    for teacher in teachers:
        this_teacher = teachers[teacher]
        if this_teacher['email']:
            bcc += this_teacher['email']

        # don't put a comma for the last entry
        if i < len(teachers) - 1:
            bcc += ", "

        i += 1

        list_of_missing_registers += '{0} {1}: {2} \n'.format(this_teacher['forename'], this_teacher['surname'],
                                                              this_teacher['form'])

    to = None
    # TODO: this could be customisable
    if str(stage) == "1":
        message = FIRST_EMAIL
    elif str(stage) == "2":
        message = SECOND_EMAIL
    elif str(stage) == "3":
        message = FINAL_EMAIL
        to = FINAL_EMAIL_TO

    # if the template uses the variable, replace is with the list of teachers
    message = message.replace('%list_of_missing_registers%', list_of_missing_registers)

    if DEBUG:
        message += "\n\nThis a debug email, the intented recipients were: " + bcc
        message += "\n\nStage " + str(stage)
        logger.debug("BCC list before we bin it: " + bcc)
        bcc = EMAIL['bcc']

    # create the email but don't send yet
    email = ISAMSEmail(message, bcc, to)

    if SEND_EMAILS:
        email.send()
    else:
        logger.debug("Email not sent as we're in debug mode")


class RegisterReminder:
    """A class to setup and execute a register reminder"""
    start_date = None
    end_date = None
    tree = None

    def __init__(self, start_date, end_date, stage):
        """RegisterReminder constructor

        :param start_date: the start of the registration period, i.e. today, in the format YYYY-MM-DD
        :param end_date: the end of the registration period, i.e. tomorrow, in the format YYYY-MM-DD
        :param stage: which stage of the reminders to run (1-3) which determines which email template to use
        """
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

        logger.debug("Filters:", filters)

        # create the connection to ISAMS and receive the parsed XML
        self.tree = connection.ISAMSConnection(URL, filters).get_tree()

        # compile a unique list of tutors with unregistered kids
        list_of_tutors = self.check_for_unregistered_students()

        # send those tutors an email to remind them
        send_tutor_emails(list_of_tutors, stage)

    def check_for_unregistered_students(self):
        """Finds unregistered students and creates a unique list of their form teachers

        :return: teachers -- a dictionary of teachers who have unregistered student
        """
        all_students = []
        reg_students = []

        for student in self.tree.iter('Pupil'):
            all_students.append(student.find('SchoolId').text)

        for leaf in self.tree.iter('RegistrationStatus'):
            reg_students.append(leaf.find('PupilId').text)

        total_students = len(all_students)
        total_registered_students = len(reg_students)

        if total_registered_students == 0:
            logger.info("No registrations found, chances are we shouldn't be running")
            sys.exit(1)

        # Remove somes students if we're in debug mode to enable us to test
        if DEBUG:
            for i in range(1, 5):
                reg_students.pop()

            logger.debug("Total students: {0}".format(total_students))
            logger.debug("Registered students: {0}".format(total_registered_students))

        # the difference between the two sets is our list of missing student IDs
        missing_students_ids = (list(set(all_students) - set(reg_students)))

        if total_students == total_registered_students:
            logger.info("No outstanding students, exiting")
            sys.exit(0)

        missing_students = []
        teachers = {}

        # loop through each student ID, finding the student, their form and their form teacher
        for student in missing_students_ids:
            try:
                leaf = self.tree.findall('.//*[SchoolId="' + student + '"]')[0]
                student_forename = leaf.find('Forename').text
                student_surname = leaf.find('Surname').text
                student_form = leaf.find('Form').text

                # add the student details to our list, not used yet
                missing_students.append(
                    {'forename': student_forename,
                     'surname': student_surname,
                     'form': student_form
                     }
                )

                form = self.tree.findall('.//Form/[@Id="' + student_form + '"]')[0]
                tutor_id = form.get('TutorId')
                logging.debug("Looking for tutor with ID {0}".format(tutor_id))

                try:
                    tutor = self.tree.findall('.//StaffMember/[@Id="' + tutor_id + '"]')[0]
                    forename = tutor.find('Forename').text
                    surname = tutor.find('Surname').text
                    form_name = student_form
                    email = tutor.find('SchoolEmailAddress').text

                    # TODO: currently doesn't send a list of students
                    if tutor_id not in teachers:
                        teachers[tutor_id] = {
                            'forename': forename,
                            'surname': surname,
                            'email': email,
                            'form': form_name}

                    logging.debug("{0} {1} {2} {3} {4}".format(student_forename, student_surname, student_form,
                                                               forename, email))

                except IndexError as e:
                    # we have a invalid (e.g. left) tutor which can happen, we have to ignore this
                    logging.warning(
                        "Error when finding the tutor of form {0}, this needs to be fixed in iSAMS".format(form))
                    logging.warning(str(e))

            except IndexError as e:
                # we have an invalid student which probably shouldn't happen unless it's an old register date
                logging.warning(
                    "Error when finding student with ID of {0}, giving up".format(student))
                logging.warning(str(e))

        return teachers


def run(stage=1):
    """Creates and runs a RegisterReminder() instance after making a few sanity checks

    :param stage: the stage of reminder to run, 1 to 3 (default 1)
    :return: None
    """
    # do some basic checks to see if we should be running
    if ENABLED:
        if DEBUG:
            RegisterReminder(DEBUG_START_DATE, DEBUG_END_DATE, stage)
        else:
            today_dt = dt.datetime.today()
            tomorrow = (today_dt + dt.timedelta(days=1)).strftime('%Y-%m-%d')
            today = today_dt.strftime('%Y-%m-%d')

            if today_dt.strftime('%Y-%m-%d') in HOLIDAYS:
                sys.exit("Today is a holiday, exiting")

            if today_dt.weekday() not in WORKING_DAYS:
                sys.exit("Today is a weekend, exiting")

            RegisterReminder(today, tomorrow, stage)
