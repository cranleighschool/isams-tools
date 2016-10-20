import logging

from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.scf import SCFConnector
from isams_tools.connectors.isams_api import iSAMSXMLConnection
from settings import SYNCPAIRS

logger = logging.getLogger('root')

def main():
    for pair in SYNCPAIRS:
        left_sync = pair[0]
        right_sync = pair[1]

        left_connection = get_connection(left_sync)

        left_connection.connect()
        right_connection = get_connection(right_sync)
        right_connection.connect()

        logger.info("Syncing {0} and {1}".format(left_sync['type'], right_sync['type']))

        # start student checks
        student_check_first_run(left_connection, right_connection)
        student_check_new_entries(left_connection, right_connection)
        student_check_for_updates(left_connection, right_connection)
        student_check_for_leavers(left_connection, right_connection)


def get_connection(pair):
    connection = None

    if pair['type'] == 'scf':
        connection = SCFConnector(pair['server'], pair['user'], pair['password'], pair['database'])
    elif pair['type'] == 'iSAMS':
        connection = iSAMSConnection(pair['server'], pair['user'], pair['password'], pair['database'])
    elif pair['type'] == 'iSAMS_XML':
        connection = iSAMSXMLConnection()

    return connection

def student_check_first_run(left, right):
    left_all_students = left.get_all_students()
    right_all_students = right.get_all_students()

    if (len(right_all_students) == 0):
        for student in left_all_students:
            right.add_student(student)

def student_check_new_entries(left, right):
    left_all_students = left.get_all_students()

    for student in left_all_students:
        if student not in right:
            right.add_student(student)
            logger.debug("New student added: {0}".format(student))


def student_check_for_updates(left, right):
    left_all_students = left.get_all_students()

    # FIXME iSAMS API has key -> value for iSAMS, need to make it consistent
    for student in left_all_students:
        in_right = student in right
        exact_match = right.exact_student_exists(student)

        if in_right and not exact_match:
            logger.debug("Student changed, updating {0}".format(student))
            right.update_student(student)

def student_check_for_leavers(left, right):
    right_all_students = right.get_all_students()

    for student in right_all_students:
        if student not in left:
            print("do_leavers_procedure(): {0}".format(student))


