import smtplib
from settings import EMAIL
from email.mime.text import MIMEText
import sys

from settings import DEBUG


class ISAMSEmail:
    msg = None

    def __init__(self, message, bcc, to=EMAIL['to'], teachers=None):
        print("DEBUG: ISAMSEmail({0}, {1}, {2}, {3})".format(message, bcc, to, teachers)) if DEBUG else False
        self.msg = MIMEText(message)
        self.msg['To'] = to
        self.msg['From'] = EMAIL['from']
        self.msg['Cc'] = EMAIL['cc']

        # if we're in debug, don't actually BCC the teachers
        # if not DEBUG and (bcc or EMAIL['bcc']):
        #     self.msg['Bcc'] = bcc + EMAIL['bcc']

        self.msg['Subject'] = EMAIL['subject']

    def send(self):
        s = smtplib.SMTP_SSL(EMAIL['server'], EMAIL['port'])
        try:
            s.login(EMAIL['username'], EMAIL['password'])
            s.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())
            s.quit()
        except Exception as exc:
            sys.exit("mail failed; {0}".format(str(exc)))
