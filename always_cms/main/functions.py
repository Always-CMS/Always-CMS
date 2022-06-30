from flask import current_app, request, abort, g, redirect
from flask_plugins import get_plugin_from_all
from datetime import datetime
from markupsafe import Markup

from always_cms.models import Post, Term, PostTerm, Type, Page
from always_cms.libs import configurations, types, menus, plugins, medias


@current_app.before_request
def before_request_func():
    if configurations.get('force_redirect_to_https').value == "True" and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
    if request.blueprint is not None and 'plugin_' in request.blueprint:
        plugin_identifier = str(request.blueprint).split('_', 1)[1]
        plugin = get_plugin_from_all(plugin_identifier)
        if not plugin.enabled:
            abort(404)
    g.always_cms_config = configurations.get_all()


def get_posts():
    return Post.query.filter(Post.status == 'publish', Post.published_at <= datetime.now()).all()


def get_posts_by_term(term):
    return Post.query.join(PostTerm).join(Term).filter(Term.name == term, PostTerm.term_id == Term.id, Post.id == PostTerm.post_id, Post.status == 'publish', Post.published_at <= datetime.now()).all()


def get_posts_by_type(type):
    return Post.query.join(Type).filter(Type.name == type, Post.type_id == Type.id, Post.status == 'publish', Post.published_at <= datetime.now()).all()


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
    get_media_url=get_media_url
    )
