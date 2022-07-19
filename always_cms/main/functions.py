# -*- coding: utf-8 -*-
"""Common functions for front-office Always-CMS"""

from flask import current_app, request, abort, g, redirect, session
from datetime import datetime
from markupsafe import Markup

from always_cms.models import *
from always_cms.libs import configurations, types, menus, plugins, medias, notifications, updater
from always_cms.app import babel, db


@current_app.before_request
def before_request_func():
    if configurations.get('force_redirect_to_https').value == "True" and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
    if request.blueprint is not None and 'plugin_' in request.blueprint:
        plugin_identifier = str(request.blueprint).split('_', 1)[1]
        plugin = plugins.get_plugin_from_all(plugin_identifier)
        if not plugin.enabled:
            abort(404)
    g.always_cms_config = configurations.get_all()


@current_app.after_request
def add_security_header(response):
    response.headers['X-Frame-Options'] = "SAMEORIGIN"
    response.headers['X-Content-Type-Options'] = "nosniff"
    response.headers['Strict-Transport-Security'] = "max-age=63072000; includeSubDomains; preload"
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


def get_posts():
    return Post.query.filter(Post.status == 'publish', Post.published_at <= datetime.now()).all()


def get_posts_by_term(term):
    return Post.query.join(PostTerm).join(Term).filter(Term.name == term, PostTerm.term_id == Term.id, Post.id == PostTerm.post_id, Post.status == 'publish', Post.published_at <= datetime.now()).all()


def get_posts_by_type(post_type):
    return Post.query.join(Type).filter(Type.name == post_type, Post.type_id == Type.id, Post.status == 'publish', Post.published_at <= datetime.now()).all()


def get_pages():
    return Page.query.filter(Page.status == 'publish', Page.published_at <= datetime.now()).all()


def date_format(standard_date):
    result = configurations.get('date_format').value
    if '%y%' in result:
        result = result.replace('%y%', str(standard_date.strftime('%y')))
    if '%d%' in result:
        result = result.replace('%d%', str(standard_date.day))
    if '%m%' in result:
        result = result.replace('%m%', str(standard_date.month))
    if '%a%' in result:
        result = result.replace('%a%', str(standard_date.strftime('%a')))
    if '%b%' in result:
        result = result.replace('%b%', str(standard_date.strftime('%b')))
    if '%Y%' in result:
        result = result.replace('%Y%', str(standard_date.year))
    if '%D%' in result:
        result = result.replace('%D%', str(standard_date.strftime('%d')))
    if '%M%' in result:
        result = result.replace('%M%', str(standard_date.strftime('%m')))
    if '%A%' in result:
        result = result.replace('%A%', str(standard_date.strftime('%A')))
    if '%B%' in result:
        result = result.replace('%B%', str(standard_date.strftime('%B')))
    return result


def get_types():
    return types.get_all()


def get_menu(location):
    return menus.get(location)


def get_header():
    return Markup(plugins.do_header())


def get_footer():
    return Markup(plugins.do_footer())


def get_field_new_post():
    return Markup(plugins.do_field_new_post())


def get_media_url(media_id):
    return medias.get_url(media_id)


def do_event(event, *args, **kwargs):
    return plugins.do_event(event, *args, **kwargs)


def do_filter(event, *args, **kwargs):
    return plugins.do_filter(event, *args, **kwargs)


def get_notifications():
    return notifications.get_available()


def new_version_available():
    return updater.new_version_available()


@current_app.context_processor
def utility_processor():
    return dict(get_posts=get_posts,
    get_posts_by_term=get_posts_by_term,
    get_posts_by_type=get_posts_by_type,
    get_pages=get_pages,
    date_format=date_format,
    get_types=get_types,
    get_menu=get_menu,
    get_header=get_header,
    get_footer=get_footer,
    get_field_new_post=get_field_new_post,
    get_media_url=get_media_url,
    do_filter=do_filter,
    do_event=do_event,
    get_notifications=get_notifications,
    new_version_available=new_version_available
    )


@babel.localeselector
def get_locale():
    if 'lang' in session and session['lang'] in current_app.config['LANGUAGES']:
        return session['lang']
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
