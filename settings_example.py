# enable or disable the whole program
ENABLED = True

# if we're in testing mode, output more debug and allow testers to add their own email
DEBUG = True

# used with above, you can check the output of emails that would have been sent
SEND_EMAILS = True

# iSAMS Batch API key
API_KEY = "11D497FF-A7D9-4646-A6B8-D9D1B8718FAC"

# iSAMS URL
URL = 'https://isams.school.com'

# Choose which connection method from: JSON, XML, MSSQL
CONNECTION_METHOD = 'JSON'

# Database settings
DATABASE_URL = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''

# specify your own dates to use when testing, e.g. a date that has already had the register taken for
DEBUG_START_DATE = '2016-09-18'
DEBUG_END_DATE = '2016-09-19'

# allows you to specify a file with XML or JSON content to test with rather tha using live data
DEBUG_DATA = 'test_data.xml'

# outgoing SMTP details
EMAIL = {
    'server': 'smtp.example.com',
    'port': 465,
    'username': 'john@company.com',
    'password': 'p455w0rd',
    'subject': 'Register not completed',
    'from': 'isams@company.com',
    'to': 'isams@company.com',
    'cc': 'reception@company.com',
    'bcc': 'manager@company.com'
}

# whether to log into the SMTP server
EMAIL_LOGIN = True

# whether to create an SSL connection or not
EMAIL_SSL = True

# Default: Monday - Friday, 0 = Mon, 6 = Sun
WORKING_DAYS = (0, 1, 2, 3, 4)

# weekdays which are not school days
# for help generating these:
# import pandas
# pandas.bdate_range('2016-12-15', '2017-01-07')
HOLIDAYS = (
    # Winter break
    '2016-12-15', '2016-12-16', '2016-12-19', '2016-12-20',
    '2016-12-21', '2016-12-22', '2016-12-23', '2016-12-26',
    '2016-12-27', '2016-12-28', '2016-12-29', '2016-12-30',
    '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
    '2017-01-06',
)

# email templates
FIRST_EMAIL = """
Dear Teacher,

This is a friendly reminder to complete your register. One or more of your students has not yet been registered.

If you are having problems completing it, please email XXX

If this message is in error, please forward to the helpdesk.

Regards,
iSAMS Bot
"""

SECOND_EMAIL = """
Dear Teacher,

There are still one or more of your students has not yet been registered.

If you are having problems completing it, please email XXX

If this message is in error, please forward to the helpdesk.

Regards,
iSAMS Bot
"""

# You can use %list_of_missing_registers% for a list in the template
FINAL_EMAIL = """
Here is a list of forms that still are oustanding:

%list_of_missing_registers%

Regards,
iSAMS Bot

"""

# separate with commas if you want more than one recipient
FINAL_EMAIL_TO = "reception@company.com"
