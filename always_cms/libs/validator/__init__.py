# -*- coding: utf-8 -*-

from email_validator import validate_email, EmailNotValidError

def email(email):
    try:
        validate_email(email).email
        return True
    except EmailNotValidError:
        return False