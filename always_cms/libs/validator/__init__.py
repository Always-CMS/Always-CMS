# -*- coding: utf-8 -*-
""" Module used for validate some data"""

from email_validator import validate_email, EmailNotValidError


def email(email_address):
    try:
        return validate_email(email_address)
    except EmailNotValidError:
        return False
