import logging

from isams_tools.connectors.core import ConnectionManager
from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.middle import MiddleConnection
from isams_tools.connectors.scf import SCFConnector
from isams_tools.connectors.isams_api import iSAMSXMLConnection
from settings import SYNCPAIRS

logger = logging.getLogger('root')

def main():
    logger.info("Starting sync")
    for pair in SYNCPAIRS:
        left_sync = pair['pair'][0]
        right_sync = pair['pair'][1]
        
        logger.info("Syncing {0} and {1}".format(left_sync['type'], right_sync['type']))

        left_connection = get_connection(left_sync)
        left_connection.connect()
        right_connection = get_connection(right_sync)
        right_connection.connect()

        if 'student' in pair['mappings']:
            logger.info('Syncing students')
            student_first_run(left_connection, right_connection)
            new_student_check(left_connection, right_connection)
            updated_student_check(left_connection, right_connection)
            left_student_check(left_connection, right_connection)

        if 'teacher' in pair['mappings']:
            logger.info('Syncing teachers')
            new_teacher_check(left_connection, right_connection)
            updated_teacher_check(left_connection, right_connection)

        if 'subject' in pair['mappings']:
            logger.info('Syncing subjects')
            new_department_check(left_connection, right_connection)
            new_subject_check(left_connection, right_connection)

        if 'year_group' in pair['mappings']:
            logger.info('Syncing year groups')
            new_year_group_check(left_connection, right_connection)

        if 'form' in pair['mappings']:
            logger.info("Syncing forms")
            new_form_check(left_connection, right_connection)


def get_connection(pair):
    connection = None

    if pair['type'] == 'scf':
        connection = SCFConnector(pair['server'], pair['user'], pair['password'], pair['database'])
    elif pair['type'] == 'iSAMS':
        connection = iSAMSConnection(pair['server'], pair['user'], pair['password'], pair['database'])
    elif pair['type'] == 'iSAMS_XML':
        connection = iSAMSXMLConnection()
    elif pair['type'] == 'middle':
        connection = MiddleConnection(pair['server'], pair['user'], pair['password'], pair['database'])
   
    return connection

def student_first_run(left, right):
    # TODO: change to a function that does a COUNT(), we don't need all the students to check there's not 0
    right_all_students = right.get_all_students()

    if (len(right_all_students) == 0):
        left_all_students = left.get_all_students()

        logger.info('No students found, running first sync')
        for student in left_all_students:
            right.add_student(student)

def new_student_check(left, right):
    left_all_students = left.get_all_students()

    for student in left_all_students:
        if student not in right:
            right.add_student(student)
            logger.debug("New student added: {0}".format(student))


def updated_student_check(left, right):
    left_all_students = left.get_all_students()

    # FIXME iSAMS API has key -> value for iSAMS, need to make it consistent
    for student in left_all_students:
        in_right = student in right
        exact_match = right.exact_student_exists(student)

        if in_right and not exact_match:
            logger.debug("Student changed, updating {0}".format(student))
            right.update_student(student)

def left_student_check(left, right):
    right_all_students = right.get_all_students()

    for student in right_all_students:
        if student not in left:
            print("do_leavers_procedure(): {0}".format(student))


def new_teacher_check(left, right):
    teachers_added = 0

    for teacher in left.get_all_teachers():
        if teacher not in right:
            right.add_teacher(teacher)
            teachers_added += 1

    logger.info("Added {0} new teachers".format(str(teachers_added)))

def updated_teacher_check(left, right):
    for teacher in left.get_all_teachers():
        right_teacher = right.get_teacher(teacher.sync_value)

        try:
            if teacher != right_teacher:
                logger.info("Updating {0} {1}".format(teacher.forename, teacher.surname))
                right.update_teacher(teacher)
        except AttributeError:
            logger.warning("Problem updating teacher: {0}".format(teacher))

def new_form_check(left, right):
    forms_added = 0

    for form in left.get_all_forms():
        if form not in right:
            logger.info("Form {0} not found, creating".format(form.name))
            right.add_form(form)
            forms_added += 1

    logger.info("Added {0} new forms".format(str(forms_added)))


def new_department_check(left, right):
    departments_added = 0

    for department in left.get_all_departments():
        if department not in right:
            logger.info("Department {0} not found, creating".format(department.name))
            right.add_department(department)
            departments_added += 1

    logger.info("Added {0} new departments".format(str(departments_added)))

def new_subject_check(left, right):
    subjects_added = 0

    for subject in left.get_all_subjects():
        if subject not in right:
            logger.info("Subject {0} not found, creating".format(subject.name))
            right.add_subject(subject)
            subjects_added += 1

    logger.info("Added {0} new departments".format(str(subjects_added)))

def new_year_group_check(left, right):
    year_groups_added = 0

    for year_group in left.get_all_year_groups():
        if year_group not in right:
            logger.info("{0} not found, creating".format(year_group.name))
            right.add_year_group(year_group)
            year_groups_added += 1

    logger.info("Added {0} new year groups".format(str(year_groups_added)))
