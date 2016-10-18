from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.scf import SCFConnector
from settings import SYNCPAIRS

def main():
    # l    eft = iSAMSConnection(ISAMS['server'], ISAMS['user'], ISAMS['password'], ISAMS['database'])
    # left.connect()
    # cursor = left.cursor
    # cursor.execute("USE ISAMS")
    # cursor.execute("SELECT * FROM TblPupilManagementPupils WHERE intSystemStatus = 1")
    # row = cursor.fetchall()
    # print(len(row))

    for pair in SYNCPAIRS:
        left_sync = pair[0]
        right_sync = pair[1]

        left_connection = get_connection(left_sync)
        left_connection.connect()
        right_connection = get_connection(right_sync)
        right_connection.connect()

        print("Syncing {0} and {1}".format(left_sync, right_sync))

        left_all_students = left_connection.get_all_students()

        right_all_students = right_connection.get_all_students()
        print(len(right_all_students))
        if (len(right_all_students) == 0):
            # first run
            for student in left_all_students:
                right_connection.add_student(student)


def get_connection(pair):
    connection = None

    if pair['type'] == 'scf':
        connection = SCFConnector(pair['server'], pair['user'], pair['password'], pair['database'])
    elif pair['type'] == 'iSAMS':
        connection = iSAMSConnection(pair['server'], pair['user'], pair['password'], pair['database'])

    return connection
