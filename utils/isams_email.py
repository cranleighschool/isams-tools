import logging
import smtplib
import sys
from email.mime.text import MIMEText

from settings import EMAIL, EMAIL_LOGIN, EMAIL_SSL

logger = logging.getLogger('root')


class ISAMSEmail:
    """Creates an email object in order to send it, named so to prevent clashes, it doesn't do anything special"""
    email = None

    def __init__(self, subject, message, to, email_from, bcc):
        self.email = MIMEText(message)
        self.email['To'] = to
        self.email['From'] = email_from
        self.email['Bcc'] = bcc
        self.email['Subject'] = subject

        logger.debug(
            "Preparing email with the following data: From: {0} To: {1} BCC: {2} Subject: {3}: ".format(
                self.email['To'], self.email['From'], self.email['Bcc'], self.email['Subject']
            ))

    def send(self):
        if EMAIL_SSL:
            s = smtplib.SMTP_SSL(EMAIL['server'], EMAIL['port'])
        else:
            s = smtplib.SMTP(EMAIL['server'], EMAIL['port'])

        try:
            if EMAIL_LOGIN:
                s.login(EMAIL['username'], EMAIL['password'])

            # concatenate recipients - BCC are just recipients not specified in To or CC
            recipients = [self.email['To'], self.email['Bcc']]
            recipients = ', '.join(filter(None, recipients))

            s.sendmail(self.email['From'], recipients, self.email.as_string())
            s.quit()
            logger.debug("Email sent successfully")
        except Exception as exc:
            logger.critical("Mail error: " + str(exc))
            sys.exit(1)
