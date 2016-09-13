import logging
import smtplib
from settings import EMAIL
from email.mime.text import MIMEText
import sys

logger = logging.getLogger('isams_tools')


class ISAMSEmail:
    msg = None

    def __init__(self, message, bcc, teachers=None):
        self.msg = MIMEText(message)
        self.msg['To'] = EMAIL['to']
        self.msg['From'] = EMAIL['from']
        self.msg['Cc'] = EMAIL['cc']
        if bcc:
            self.msg['Bcc'] = bcc
        self.msg['Subject'] = EMAIL['subject']
        logger.debug("Preparing email with the following headers:\nFrom:{0}\nTo:{1}\nCC:{2}\nBCC:{3}\nSubject{4}".format(
            EMAIL['to'], EMAIL['from'], EMAIL['cc'], bcc, EMAIL['subject']
        ))
        logger.debug("\n{0}".format(message))

    def send(self):
        s = smtplib.SMTP_SSL(EMAIL['server'], EMAIL['port'])
        try:
            s.login(EMAIL['username'], EMAIL['password'])
            s.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())
            s.quit()
            logger.debug("Email sent successfully")
        except Exception as exc:
            sys.exit("mail failed; {0}".format(str(exc)))
            logger.info("Mail error: {0}".format(str(exc)))
