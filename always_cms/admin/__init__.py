# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template

from always_cms.libs.roles import register_context_processors
from always_cms.libs.posts import count as posts_count
from always_cms.libs.comments import count as comments_count
from always_cms.libs.pages import count as pages_count
from always_cms.libs.users import count as users_count

from always_cms.libs import types as types_class

from always_cms.models import Model

from .routes import admin
from . import users
from . import medias
from . import plugins
from . import themes
from . import posts
from . import pages
from . import configurations
from . import terms
from . import types
from . import comments
from . import menus

register_context_processors()


@admin.route('/admin/')
@admin.route('/admin/index')
@login_required
def index():
    default_type_post = types_class.get_all()[0].id
    default_model_post = Model.query.all()[0].id

    return render_template('index.html', posts_count=posts_count(), comments_count=comments_count(),
        pages_count=pages_count(), users_count=users_count(), default_type_post=default_type_post,
        default_model_post=default_model_post)


@admin.app_errorhandler(404)
def page_not_found(error):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@admin.app_errorhandler(403)
def page_forbidden(error):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403
