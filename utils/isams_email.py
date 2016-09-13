import smtplib
from settings import EMAIL
from email.mime.text import MIMEText
import sys

from settings import DEBUG


class ISAMSEmail:
    msg = None

    def __init__(self, message, bcc, teachers=None):
        self.msg = MIMEText(message)
        self.msg['To'] = EMAIL['to']
        self.msg['From'] = EMAIL['from']
        self.msg['Cc'] = EMAIL['cc']
        self.msg['Subject'] = EMAIL['subject']

    def send(self):
        s = smtplib.SMTP_SSL(EMAIL['server'], EMAIL['port'])
        try:
            s.login(EMAIL['username'], EMAIL['password'])
            s.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())
            s.quit()
        except Exception as exc:
            sys.exit("mail failed; {0}".format(str(exc)))
