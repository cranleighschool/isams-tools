import logging
import pickle
from pathlib import Path

from settings import URL, DEBUG
from utils import connection


# # make sure this isn't called directly
# if __name__ == "__main__":
#     sys.stderr.write('Please use bin/isams_tools instead\n')
#     sys.exit(1)

logger = logging.getLogger('root')


class ADSync:
    tree = None

    def __init__(self):
        # filters that are required by iSAMS for this request TODO: move to connection?
        filters = """<?xml version='1.0' encoding='utf-8'?>
        <Filters>
            <RegistrationManager>
                <RegistrationStatus startDate="{0}" endDate="{1}" />
            </RegistrationManager>
        </Filters>
        """.format("2016-09-08", "2016-09-09")

        logger.debug("Filters:" + filters)

        # create the connection to ISAMS and receive the parsed XML
        self.tree = connection.ISAMSConnection(URL, filters).get_tree()

        first_run = True

        previous_students = []
        all_students = []

        student_file = Path("current_students.txt")
        if student_file.is_file():
            previous_students = pickle.load(open("current_students.b", "rb"))
            first_run = False

        if DEBUG:
            last_student = None

        for student in self.tree.iter('Pupil'):
            id = student.find('SchoolId').text
            username = student.find('UserName').text
            email = student.find('EmailAddress').text
            email_first_bit = email.split('@')[0]
            if username != email_first_bit:
                print("Warning {0} != {1}".format(username, email_first_bit))
            forename = student.find('Forename').text
            surname = student.find('Surname').text

            student_details = {'id': id, 'username': username, 'email': email, 'forename': forename, 'surname': surname}
            all_students.append(student_details)


        temp_student = None

        if not first_run:
            if DEBUG:
                temp_student = all_students.pop()

            new_students = [x for x in all_students if x not in previous_students]
            leavers = [x for x in previous_students if x not in all_students]
            if len(new_students) > 0:
                print("Student(s) have joined")
                print(new_students)
            if len(leavers) > 0:
                print("Student(s) have left")
                print(leavers)

        if DEBUG:
            all_students.append(temp_student)

        pickle.dump(all_students, open("current_students.b", "wb"))

        logger.debug("Total students: " + str(len(all_students)))