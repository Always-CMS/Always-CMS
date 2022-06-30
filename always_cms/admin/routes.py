# -*- coding: utf-8 -*-

from os import path
from flask import Blueprint, current_app

admin = Blueprint('admin', __name__, template_folder=path.join(
    current_app.config['DEFAULT_FOLDER'], "templates/admin"))
