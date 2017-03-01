import logging

from isams_tools.connectors.isams import iSAMSConnection
from settings import ISAMS_DATABASE, ISAMS_DATABASE_SERVER, ISAMS_DATABASE_USER, ISAMS_DATABASE_PASS, DATA_CHECK_ENABED, \
    DATA_CHECK_IGNORE_SUBJECTS, DATA_CHECK_FAIL_EMAIL
from isams_tools.utils.isams_email import ISAMSEmail

duplicate_pupil_in_sets = {
'title': "Pupils in set twice",
'notify': "khogg@cranleigh.ae",
'query': """
SELECT
	A.*
	,B.*
	,S.txtName AS [Set Code]
FROM
	iSAMS.dbo.TblTeachingManagerSetLists A
	INNER JOIN iSAMS.dbo.TblTeachingManagerSetLists B
		ON B.txtSchoolID=A.txtSchoolID
		AND B.intSetID=A.intSetID
		AND B.TblTeachingManagerSetListsID > A.TblTeachingManagerSetListsID
	LEFT JOIN iSAMS.dbo.TblTeachingManagerSets S
		ON S.TblTeachingManagerSetsID=A.intSetID
""", 'email': """
The following students have multiple entries for sets:

{0}

"""}

teacher_timetable_mismatches = {
'title': "Teachers not assigned to correct sets",
'notify': "khogg@cranleigh.ae",
'query': """
	SELECT
	Sets.txtSetCode
	,Sets.txtTeacher
	,TTS.txtTeacher
	,S1.Fullname AS [Set Teacher]
	,S2.Fullname AS [Timetable Teacher]
	,Sub.txtSubjectName
FROM
	TblTeachingManagerSets Sets
	INNER JOIN TblStaff S1
		ON S1.User_Code=Sets.txtTeacher
	INNER JOIN TblTimetableManagerSchedule TTS
		ON TTS.txtCode=Sets.txtSetCode
	INNER JOIN TblStaff S2
		ON S2.User_Code=TTS.txtTeacher
	LEFT JOIN TblTeachingManagerSubjects Sub
		ON Sub.TblTeachingManagerSubjectsID=Sets.intSubject
WHERE
	Sets.txtTeacher NOT IN (
		SELECT txtTeacher FROM TblTimetableManagerSchedule
		WHERE txtCode = Sets.txtSetCode
	)
	AND Sub.txtSubjectName NOT IN %s

""", 

'params': DATA_CHECK_IGNORE_SUBJECTS,
'email': """
The following teachers are teaching a lesson but not added as a set teacher:

{0}

"""}

duplicate_reports = {
'title': "Duplicate report entries",
'notify': "jcarney@cranleigh.ae",
'query': """
SELECT
	*
FROM (
	SELECT
		AR.txtReportCycleName AS [Assessment Point]
		,AR.intReportCycleID AS [Cycle ID]
		,AR.[txtID] AS [Subject]
		,AR.[intNCYear] AS [NC Year ID]
		,AR.[txtSubID] AS [Set]
		,AR.[txtSchoolID] AS [ID]
		,AR.txtForename AS [Forename]
		,AR.txtSurname AS [Surname]
		,AR.[txtSubmitByInitials] AS [Submitted By]
		,AR.[dtSubmittedOn] AS [Submitted]
		,AR.[txtGradingName] AS [Grade Type]
		,AR.[txtGrade] AS [Grade]
		,AR.[TblReportsStoreID] AS [ReportID]
		,ROW_NUMBER() over(partition by intReportCycleID		-- Use partition to highlight any duplicates
										,intID
										,AR.txtSchoolID
										,txtGradingName
									order by intReportProgress, dtSubmittedOn) AS [Report_Order]
		FROM
			[iSAMS].[dbo].[VwReportsManagementAcademicReports] AR
		WHERE
			[txtGradingName] is not null
			AND [intReportProgress]=1
			AND AR.intReportCycleAcademicYear=2016
			AND AR.txtGradingName='Attainment'
            AND AR.intReportTypeID=1
	) AS Grades
WHERE
	Grades.Report_Order > 1
""", 'email': """
The following students have multiple entries for reports:

{0}

"""}

pupils_in_two_sets = {
'title': "Pupil in two subject sets",
'notify': "khogg@cranleigh.ae",
'query': """
SELECT
	PMP.txtSchoolID AS [iSAMS ID]
	,PMP.txtFullName AS [Pupil]
	,Sub.txtSubjectName AS [Subject]
	,A.txtSubmitBy [Entry 1]
	,A.txtSubmitDateTime [Entered 1]
	,S1.txtName AS [Set 1 Code]
	,B.txtSubmitBy AS [Entry 2]
	,B.txtSubmitDateTime AS [Entered 2]
	,S2.txtName AS [Set 2 Code]
FROM
	iSAMS.dbo.TblTeachingManagerSetLists A
	INNER JOIN iSAMS.dbo.TblTeachingManagerSetLists B
		ON B.txtSchoolID=A.txtSchoolID
		AND B.intSetID <> A.intSetID
		AND B.TblTeachingManagerSetListsID > A.TblTeachingManagerSetListsID
	LEFT JOIN iSAMS.dbo.TblTeachingManagerSets S1
		ON S1.TblTeachingManagerSetsID=A.intSetID
	LEFT JOIN iSAMS.dbo.TblTeachingManagerSets S2
		ON S2.TblTeachingManagerSetsID=B.intSetID
	LEFT JOIN TblTeachingManagerSubjects Sub
		ON Sub.TblTeachingManagerSubjectsID=S1.intSubject
	LEFT JOIN TblPupilManagementPupils PMP
		ON PMP.txtSchoolID=A.txtSchoolID
WHERE
	S1.intSubject=S2.intSubject
	AND txtSubjectName NOT in %s
""", 'email': """
The following students are in two sets for the same subject:

{0}

""", 'params': DATA_CHECK_IGNORE_SUBJECTS}

pupils_with_no_usernames = {
'title': "Missing username/email",
'notify': "helpdesk@cranleigh.ae",
'query': """
SELECT txtForename, txtSurname FROM TblPupilManagementPupils 
WHERE intSystemStatus = 1
AND (txtEmailAddress = '' OR txtUserName = '')
""",
'email': """
The following students have no username or email:

{0}

""",
}

checks = [duplicate_reports, duplicate_pupil_in_sets, teacher_timetable_mismatches, pupils_in_two_sets, pupils_with_no_usernames]

logger = logging.getLogger('root')

def run():
    if DATA_CHECK_ENABED:
        logger.info("Starting data checks")
        connection = iSAMSConnection(ISAMS_DATABASE_SERVER, ISAMS_DATABASE_USER, ISAMS_DATABASE_PASS, ISAMS_DATABASE)
        connection.connect()
        cursor = connection.cursor

        email = ""

        for check in checks:
            data = ""
            if 'params' in check:
                cursor.execute(check['query'], (check['params'],))
            else:
                cursor.execute(check['query'])

            rows = cursor.fetchall()
            if len(rows) > 0:
                logger.debug("Check failed, data:")
                for row in rows:
                    logger.debug("{0}".format(row))
                    # flatten the dict values, each query returns different keys so this is the best we can do
                    data += ', '.join("{!s}".format(val) for (key,val) in row.items()) + '\n'

                email = check['email'].format(data)

            if email:
                to = DATA_CHECK_FAIL_EMAIL
                if check['notify']:
                    to = check['notify']
                    
                ISAMSEmail("[iSAMS Data] " + check['title'], email, to, "isams@cranleigh.ae").send()
            else:
                logger.info("No errors found with the data")
            
            email = ""


