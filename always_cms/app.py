# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.event import listen
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_dropzone import Dropzone
from flask_babel import Babel
from flask_minify import Minify
from always_cms.libs.plugins import PluginManager
from always_cms.libs.templates import TemplateManager
from always_cms.libs.shortcodes import Shortcodes
from flask_ckeditor import CKEditor
from flask_qrcode import QRcode

from os import path

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
plugin_manager = PluginManager()
template_manager = TemplateManager()
ckeditor = CKEditor()
shortcodes = Shortcodes()
babel = Babel()
minify = Minify()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    app.config['VERSION'] = '1.0.0'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['DROPZONE_ENABLE_CSRF'] = True
    app.config['DEFAULT_FOLDER'] = path.abspath(path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = path.join(
    app.config['DEFAULT_FOLDER'], 'uploads')
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'languages'
    app.config['CKEDITOR_FILE_UPLOADER'] = '/admin/medias'
    app.config['CKEDITOR_FILE_BROWSER'] = '/admin/medias'
    app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
    app.config['CKEDITOR_ENABLE_CSRF'] = True

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import Configuration, User, create_tables

    login_manager = LoginManager()
    login_manager.blueprint_login_views = {
        'admin': '/admin/login',
        'main': '/login'
    }
    login_manager.init_app(app)

    Dropzone(app)

    csrf.init_app(app)

    babel.init_app(app)

    ckeditor.init_app(app)

    QRcode(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(user_id)

    with app.app_context():
        # init database
        create_tables()

        # blueprint for admin routes
        from .admin import routes as admin_blueprint
        app.register_blueprint(admin_blueprint.admin)

        # blueprint for non-auth routes
        from .main import routes as main_blueprint
        app.register_blueprint(main_blueprint.main)

        app.config['TEMPLATE'] = Configuration.query.filter_by(
            name='template').first().value

        if Configuration.query.filter_by(name='minify_template').first().value == 'True':
            minify.init_app(app)
            minify.html = True
            minify.js = True
            minify.cssless = True
        else:
            minify.init_app(app)
            minify.html = False
            minify.js = False
            minify.cssless = False

    plugin_manager.init_app(app)

    template_manager.init_app(app)

    return app
