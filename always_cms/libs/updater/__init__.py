# -*- coding: utf-8 -*-

from flask import current_app
from requests import get


def get_last_release():
    try:
        response = get("https://api.github.com/repos/Always-CMS/Always-CMS/releases/latest")
        return response.json()["name"]
    except:
        return None


def new_version_available():
    current_version = current_app.config['VERSION']
    last_version = get_last_release()
    if last_version != None and last_version != current_version:
        return last_version
    else:
        return False