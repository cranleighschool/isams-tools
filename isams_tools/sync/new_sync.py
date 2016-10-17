from isams_tools.connectors.isams import iSAMSConnection
from isams_tools.connectors.scf import SCFConnector
from settings import ISAMS, SCF

def main():
    # l    eft = iSAMSConnection(ISAMS['server'], ISAMS['user'], ISAMS['password'], ISAMS['database'])
    # left.connect()
    # cursor = left.cursor
    # cursor.execute("USE ISAMS")
    # cursor.execute("SELECT * FROM TblPupilManagementPupils WHERE intSystemStatus = 1")
    # row = cursor.fetchall()
    # print(len(row))
    isams = iSAMSConnection(ISAMS['server'], ISAMS['user'], ISAMS['password'], ISAMS['database'])
    isams.connect()
    isams_all_students = isams.get_all_students()

    scf = SCFConnector()
    scf.connect()
    scf_all_students = scf.get_all_students()
    if (len(scf_all_students) == 0):
        # first run
        for student in isams_all_students:
            scf.add_student(student)

    scf.connection.commit()
    scf.connection.close()


