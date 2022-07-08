# -*- coding: utf-8 -*-
""" Emailer module used by Always-CMS"""

import smtplib
from email.utils import formatdate

from always_cms.libs import configurations


def send(title, message, toaddrs = []):
    if configurations.get('mail_secure').value == 'SSL':
        server = smtplib.SMTP_SSL()
    else:
        server = smtplib.SMTP()

    server.connect( configurations.get('mail_host').value, configurations.get('mail_port').value )

    if configurations.get('mail_secure').value == 'False':
        server.helo()
    else:
        server.ehlo()

    fromaddr = configurations.get('mail_username').value

    if configurations.get('mail_password').value != '':
        password = configurations.get('mail_password').value
        server.login(fromaddr, password)

    msg = """\
    From: %s\r\n\
    To: %s\r\n\
    Subject: %s\r\n\
    Date: %s\r\n\
    \r\n\
    %s
    """ % (fromaddr, ", ".join(toaddrs), title, formatdate(localtime=True), message)
    print(msg, flush=True)
    #try:
    res = server.sendmail(fromaddr, toaddrs, msg)
    print(res, flush=True)
    server.quit()
    return True
    #except smtplib.SMTPException:
    #    return False
