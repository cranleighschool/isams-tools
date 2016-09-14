# enable or disable the whole program
ENABLED = True

# if we're in testing mode, output more debug and allow testers to add their own email
DEBUG = True

# specify your own dates to use when testing, e.g. a date that has already had the register taken for
DEBUG_START_DATE = '2016-09-01'
DEBUG_END_DATE = '2016-09-02'

# used with above, you can check the output of emails that would have been sent
SEND_EMAILS = False

# outgoing SMTP details, bcc will be appended to the list of teachers
EMAIL = {
    'server': 'smtp.example.com',
    'port': 465,
    'username': 'john@company.com',
    'password': 'p455w0rd',
    'subject': 'Register not completed',
    'from': 'isams@company.com',
    'to': 'isams@company.com',
    'cc': '',
    'bcc': 'reception@company.com, ',  # make sure the list ends with a comma
}

# iSAMS REST API key
key = "93FSGD-FDSFS2-VRECSF-2FD3VF"

# iSAMS URL, be sure to end with ?apiKey={{{0}}} to allow for the api key to be replace
URL = 'https://isams.company.com/api/batch/1.0/xml.ashx?apiKey={{{0}}}'
URL = URL.format(key)

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

FINAL_EMAIL_TO = "reception@company.com"
