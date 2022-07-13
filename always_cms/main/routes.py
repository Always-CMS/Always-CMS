# -*- coding: utf-8 -*-

from os import path
from urllib.parse import urlparse
from flask_login import login_required, current_user
from flask import Blueprint, render_template, url_for, redirect, flash, current_app, send_from_directory, abort, session
from flask import make_response, request
from jinja2.exceptions import TemplateNotFound
from always_cms.models import Post, Page, Type, Term
from always_cms.app import shortcodes
from always_cms.libs import configurations

from . import functions

main = Blueprint('main', __name__,
                 template_folder=path.join(current_app.config['DEFAULT_FOLDER'], "templates/"))


@main.route('/')
@main.route('/index', strict_slashes=False)
def index():
    return render_template('%s/posts.html' % current_app.config['TEMPLATE'])


@main.route('/post/<type>', strict_slashes=False)
def type(type):
    if Type.query.filter_by(name=type).count() != 0:
        try:
            return render_template('%s/type_%s.html' % (current_app.config['TEMPLATE'], type), type=type)
        except TemplateNotFound:
            return render_template('%s/types.html' % current_app.config['TEMPLATE'], type=type)
    else:
        abort(404)


@main.route('/term/<term>', strict_slashes=False)
def terms(term):
    if Term.query.filter_by(name=term).count() != 0:
        try:
            return render_template('%s/term_%s.html' % (current_app.config['TEMPLATE'], term), term=term)
        except TemplateNotFound:
            return render_template('%s/terms.html' % current_app.config['TEMPLATE'], term=term)
    else:
        abort(404)


@main.route('/assets/<filename>')
def assets_img(filename):
    asset_path = path.join(
        current_app.config['DEFAULT_FOLDER'], "templates/classic/assets/")
    return send_from_directory(asset_path, filename)


@main.route('/assets/css/<filename>')
def assets_css(filename):
    asset_path = path.join(
        current_app.config['DEFAULT_FOLDER'], "templates/classic/assets/css/")
    return send_from_directory(asset_path, filename)


@main.route('/assets/js/<filename>')
def assets_js(filename):
    asset_path = path.join(
        current_app.config['DEFAULT_FOLDER'], "templates/classic/assets/js/")
    return send_from_directory(asset_path, filename)


@main.route('/uploads/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(path, filename)


@main.app_errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('%s/404.html' % current_app.config['TEMPLATE']), 404


@main.route('/post/<type>/<permalink>', strict_slashes=False)
def get_post_content(type, permalink):
    post = Post.query.filter_by(permalink=permalink).first()
    post.body = shortcodes.do_shortcode(post.body)
    if post:
        if post.model_id and post.model.name != "Default":
            try:
                return render_template('%s/model_%s.html' % (current_app.config['TEMPLATE'], post.model.slug), post=post)
            except TemplateNotFound:
                return render_template('%s/post.html' % current_app.config['TEMPLATE'], post=post)
        else:
            try:
                return render_template('%s/type_%s.html' % (current_app.config['TEMPLATE'], post.type.slug), post=post)
            except TemplateNotFound:
                return render_template('%s/post.html' % current_app.config['TEMPLATE'], post=post)
    else:
        abort(404)


@main.route('/page/<permalink>', strict_slashes=False)
def get_page_content(permalink):
    page = Page.query.filter_by(permalink=permalink).first()
    page.body = shortcodes.do_shortcode(page.body)
    if page:
        return render_template('%s/page.html' % current_app.config['TEMPLATE'], page=page)
    else:
        abort(404)


@main.route("/sitemap")
@main.route("/sitemap/")
@main.route("/sitemap.xml")
def sitemap():
    """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
    """

    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc

    # Static routes with static content
    static_urls = []
    for rule in current_app.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/user") and not str(rule).startswith("/sitemap"):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}"
                }
                static_urls.append(url)

    # Dynamic routes with dynamic content
    dynamic_urls = []
    blog_posts = functions.get_posts()

    for post in blog_posts:
        if post.updated_at is None:
            updated_at = post.created_at
        else:
            updated_at = post.updated_at
        url = {
            "loc": f"%s/%s/%s" % (host_base, post.type.slug, post.permalink),
            "lastmod": updated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        dynamic_urls.append(url)

    pages = functions.get_pages()

    for page in pages:
        if page.updated_at is None:
            updated_at = page.created_at
        else:
            updated_at = page.updated_at
        url = {
            "loc": f"%s/page/%s" % (host_base, page.permalink),
            "lastmod": updated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        dynamic_urls.append(url)

    xml_sitemap = render_template(
        "sitemap.xml", static_urls=static_urls, dynamic_urls=dynamic_urls, host_base=host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response


@main.route('/robots.txt')
def robots():
    content = configurations.get('robots_txt')
    response = make_response(content.value)
    return response


@main.route("/lang/<language_code>")
def set_language(language_code):
    if language_code in current_app.config['LANGUAGES']:
        session['lang'] = language_code
    return redirect(url_for('main.index'))