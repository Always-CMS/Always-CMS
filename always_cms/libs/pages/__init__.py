# -*- coding: utf-8 -*-

from flask_login import current_user
from flask import flash, abort
from flask_babel import gettext
from slugify import slugify
from sqlalchemy.sql import func

from always_cms.libs import plugins
from always_cms.libs.posts import get_schedule
from always_cms.app import db
from always_cms.models import Page


def get_all():
    return Page.query.all()


def get(page_id):
    page = Page.query.filter_by(id=page_id).first()
    if page:
        return page
    else:
        abort(404)


def add(title, body, description, status, schedule=None):

    data = locals()
    data['permalink'] = slugify(data['title'])

    data = plugins.do_filter("before_page_add", data)

    if Page.query.filter_by(permalink=data['permalink']).first():
        flash(gettext('This permalink is already in use. Please change title.'), 'warning')
    elif data['status'] not in ['draft', 'private', 'publish']:
        flash(gettext('This status is not accepted.'), 'warning')
    else:
        data['schedule'] = get_schedule(data['schedule'], data['status'])

        new_page = Page(permalink=data['permalink'],
                        title=data['title'],
                        body=data['body'],
                        description=data['description'],
                        status=data['status'],
                        published_at=data['schedule'],
                        author_id=current_user.id
                        )

        # add the new page to the database
        db.session.add(new_page)
        db.session.commit()
        plugins.do_event("after_page_add", new_page)
        flash(gettext('Your page has been successfully created.'), 'success')
        return new_page

    return False


def edit(page_id, title, body, description, status, schedule=None):

    data = locals()
    data['permalink'] = slugify(data['title'])

    data = plugins.do_filter("before_page_edit", data)

    get_page = Page.query.filter_by(permalink=data['permalink']).first()

    if get_page is not None and str(get_page.id) != data['page_id']:
        flash(gettext('This permalink is already in use. Please change title.'), 'warning')
    else:
        data['schedule'] = get_schedule(data['schedule'], data['status'])
        
        Page.query.filter_by(id=data['page_id']).update(dict(permalink=data['permalink'],
                                                             title=data['title'],
                                                             body=data['body'],
                                                             description=data['description'],
                                                             status=data['status'],
                                                             published_at=data['schedule']
                                                             ))
        db.session.commit()
        flash(gettext('Your post has been successfully edited.'), 'success')
        plugins.do_event("after_page_edit", data)
        return True
    return False


def delete(page_id):
    plugins.do_event("before_page_delete", locals())
    Page.query.filter_by(id=page_id).delete()
    db.session.commit()
    flash(gettext('Your page has been successfully deleted.'), 'success')
    plugins.do_event("after_page_delete", locals())


def count(status=None):
    if status is None:
        return Page.query.count()
    return Page.query.filter_by(status=status).count()
