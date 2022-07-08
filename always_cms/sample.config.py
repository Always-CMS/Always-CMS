# -*- coding: utf-8 -*-
"""Sample of configuration file required for Always-CMS"""

# SQL settings -  You can get this info from your web host
SQLALCHEMY_DATABASE_URI = 'mysql://USERNAME:PASSWORD@HOSTNAME/DATABASE'

# Change these to different unique phrases!
SECRET_KEY = 'YOUR-SECRET-KEY'

# Allowed extensions for upload forms
ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',  # Images
    'pdf', 'doc', 'docx', 'odt', 'xls', 'xlsx', 'key', 'ppt', 'pptx', 'pps', 'ppsx',  # Documents
    'mp3', 'm4a', 'ogg', 'wav',  # Audio
    'mp4', 'm4v', 'mov', 'avi', 'mpg', 'ogv', '3gp', '3g2'  # Video
}

BABEL_DEFAULT_LOCALE = 'en'

# For developers: debugging mode.
DEBUG = False
